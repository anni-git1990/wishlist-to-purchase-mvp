"""
End-to-End User Journey Integration Test Suite
Validates the 3 core end-to-end user journeys defined in myntra_mvp_context (1).md & architecture.md:
1. Primary Journey: Wishlist Add -> Revisit -> Fit/Quality Sheet -> Size Select -> Bag -> Purchase (30-day attribution).
2. Trigger-Assisted Journey: Save Item -> Restock Trigger -> Push Deep Link -> Fit Sheet -> Purchase.
3. Fallback Journey: Zero Reviews -> Fallback to Brand Size Chart without breaking UI.
"""

import sys
import os
import unittest
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.ab_assignment_service import ABAssignmentService
from services.event_ingestion_service import EventIngestionService
from services.fit_confidence_service import FitConfidenceService
from services.quality_digest_service import QualityDigestService
from services.trigger_evaluation_service import TriggerEvaluationService
from mobile_views.fit_confidence_views import NativeMobileFitViewRenderer
from mobile_views.quality_digest_views import NativeMobileQualityViewRenderer


class TestEndToEndUserJourneys(unittest.TestCase):

    def setUp(self):
        self.ab_svc = ABAssignmentService()
        self.ingest_svc = EventIngestionService()
        self.fit_svc = FitConfidenceService()
        self.quality_svc = QualityDigestService()
        self.trigger_svc = TriggerEvaluationService()
        self.fit_renderer = NativeMobileFitViewRenderer()
        self.quality_renderer = NativeMobileQualityViewRenderer()

    def test_primary_user_journey(self):
        uid = "usr_98745210"
        pid = "style_3948102"
        sku = "sku_991823"

        # 1. User discovers & adds item to wishlist
        assignment = self.ab_svc.get_assignment(uid)
        ok1, msg1 = self.ingest_svc.ingest_event({
            "eventId": "evt_p1",
            "eventName": "wishlist_item_added",
            "timestamp": "2026-09-04T10:00:00Z",
            "userId": uid,
            "productId": pid,
            "variantId": sku,
            "sourceSurface": "PDP",
            "experimentGroup": assignment["experimentGroup"]
        })
        self.assertTrue(ok1)

        # 2. User revisits wishlist
        fit_res = self.fit_svc.get_fit_confidence(pid, uid)
        chip_view = self.fit_renderer.render_surface1_wishlist_fit_chip(fit_res)
        self.assertTrue(chip_view["showSizeChip"])
        self.assertEqual(chip_view["selectedSize"], "M")

        # 3. User opens Fit Detail Sheet & selects recommended size
        sheet_view = self.fit_renderer.render_surface2_fit_detail_sheet(fit_res)
        self.assertFalse(sheet_view["isFallback"])
        self.assertEqual(len(sheet_view["widgets"]), 5)

        # 4. User adds recommended size to bag
        ok2, _ = self.ingest_svc.ingest_event({
            "eventId": "evt_p2",
            "eventName": "wishlist_item_added_to_bag",
            "timestamp": "2026-09-04T10:05:00Z",
            "userId": uid,
            "productId": pid,
            "selectedSize": "M",
            "daysSinceWishlistAdd": 0,
            "experimentGroup": assignment["experimentGroup"]
        })
        self.assertTrue(ok2)

        # 5. User completes purchase
        ok3, _ = self.ingest_svc.ingest_event({
            "eventId": "evt_p3",
            "eventName": "wishlisted_item_purchased",
            "timestamp": "2026-09-04T10:10:00Z",
            "userId": uid,
            "orderId": "ord_primary_1001",
            "productId": pid,
            "selectedSize": "M",
            "recommendedSize": "M",
            "daysSinceWishlistAdd": 0,
            "experimentGroup": assignment["experimentGroup"],
            "wasPurchasedWithin30Days": True
        })
        self.assertTrue(ok3)

        # Verify Attribution
        summary = self.ingest_svc.get_attribution_summary()
        group = summary["treatment"] if assignment["isTreatment"] else summary["control"]
        self.assertEqual(group["purchasers30d"], 1)

    def test_trigger_assisted_user_journey(self):
        uid = "usr_trigger_01"
        pid = "style_3948102"
        sku = "sku_991823"

        # 1. User saves item
        assignment = self.ab_svc.get_assignment(uid)
        self.ingest_svc.ingest_event({
            "eventId": "evt_t1",
            "eventName": "wishlist_item_added",
            "timestamp": "2026-08-20T10:00:00Z",
            "userId": uid,
            "productId": pid,
            "variantId": sku,
            "sourceSurface": "PDP",
            "experimentGroup": assignment["experimentGroup"]
        })

        # 2. Trigger Event fires
        eval_res = self.trigger_svc.evaluate_trigger_event({
            "productId": pid,
            "triggerEventType": "NEW_FIT_EVIDENCE",
            "minNewReviews": 3
        })
        self.assertGreater(eval_res["usersEvaluated"], 0)

        # 3. User opens push notification deep link
        ok_open, _ = self.ingest_svc.ingest_event({
            "eventId": "evt_t2",
            "eventName": "wishlist_trigger_opened",
            "timestamp": "2026-08-21T09:00:00Z",
            "userId": uid,
            "productId": pid,
            "triggerType": "NEW_FIT_EVIDENCE",
            "channel": "APNS",
            "timeToOpenSeconds": 3600
        })
        self.assertTrue(ok_open)

    def test_fallback_user_journey(self):
        uid = "usr_fallback_01"
        pid = "style_zero_reviews"

        # Fetch zero-review product
        fit_res = self.fit_svc.get_fit_confidence(pid, uid, review_count=0)
        self.assertTrue(fit_res["fallbackState"]["isFallbackActive"])

        # Render Surface 1 & 2 in fallback state
        chip_view = self.fit_renderer.render_surface1_wishlist_fit_chip(fit_res)
        self.assertEqual(chip_view["badgeText"], "Limited Evidence")
        self.assertFalse(chip_view["showSizeChip"])

        sheet_view = self.fit_renderer.render_surface2_fit_detail_sheet(fit_res)
        self.assertTrue(sheet_view["isFallback"])
        self.assertEqual(sheet_view["widgets"][0]["widgetType"], "FallbackMessageWidget")


if __name__ == "__main__":
    unittest.main()
