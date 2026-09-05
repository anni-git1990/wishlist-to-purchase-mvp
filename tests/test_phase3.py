"""
Unit and Integration Test Suite for Phase 3 Deliverables (Fit Confidence Layer MVP)
Tests:
1. FitRecommendationEngine ML Inference & Confidence Scoring.
2. FitConfidenceService Endpoint Latency SLA (<45ms) & Caching.
3. Fallback Orchestration for Products with Zero Reviews.
4. Recommendation Feedback Submission (POST /confidence-feedback).
5. Native Mobile UI View Model Renderer (Surface 1 & Surface 2).
"""

import sys
import os
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml_services.fit_recommendation_engine import FitRecommendationEngine
from services.fit_confidence_service import FitConfidenceService
from mobile_views.fit_confidence_views import NativeMobileFitViewRenderer


class TestPhase3Deliverables(unittest.TestCase):

    def setUp(self):
        self.engine = FitRecommendationEngine()
        self.service = FitConfidenceService()
        self.renderer = NativeMobileFitViewRenderer()

    def test_fit_recommendation_engine_high_confidence(self):
        user_vector = {
            "height_cm": 178,
            "weight_kg": 74,
            "chest_cm": 98,
            "brand_order_history": {"Roadster": {"M": {"purchased": 4, "returned_size": 0}}}
        }
        product_data = {
            "productId": "style_3948102",
            "brandId": "Roadster",
            "reviewCount": 184,
            "similarBodyReviewCount": 5,
            "hasSizeChart": True
        }

        res = self.engine.recommend_size(user_vector, product_data)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["personalization"]["confidenceLevel"], "HIGH")
        self.assertEqual(res["personalization"]["recommendedSize"], "M")
        self.assertEqual(res["personalization"]["fitMatchPercentage"], 88)
        self.assertFalse(res["fallbackState"]["isFallbackActive"])

    def test_fit_recommendation_engine_zero_reviews_fallback(self):
        user_vector = {"height_cm": 178, "weight_kg": 74}
        product_data = {
            "productId": "style_new_001",
            "brandId": "Roadster",
            "reviewCount": 0,
            "similarBodyReviewCount": 0,
            "hasSizeChart": True
        }

        res = self.engine.recommend_size(user_vector, product_data)
        self.assertEqual(res["personalization"]["confidenceLevel"], "LIMITED_EVIDENCE")
        self.assertIsNone(res["personalization"]["recommendedSize"])
        self.assertTrue(res["fallbackState"]["isFallbackActive"])

    def test_fit_confidence_service_latency_and_caching(self):
        # First call (Cold cache)
        res1 = self.service.get_fit_confidence("style_3948102", "usr_98745210")
        self.assertIn("latencyMs", res1)
        self.assertTrue(res1["slaMet"], f"Latency {res1['latencyMs']}ms exceeded 45ms SLA target")
        self.assertFalse(res1["fromCache"])

        # Second call (Cached hit)
        res2 = self.service.get_fit_confidence("style_3948102", "usr_98745210")
        self.assertTrue(res2["fromCache"])
        self.assertLess(res2["latencyMs"], 15.0)

    def test_submit_confidence_feedback(self):
        fb_res = self.service.submit_confidence_feedback("style_3948102", {
            "userId": "usr_98745210",
            "feature": "FIT_CONFIDENCE",
            "recommendedSize": "M",
            "selectedSize": "L",
            "helpful": False,
            "issueType": "RECOMMENDED_TOO_SMALL"
        })
        self.assertEqual(fb_res["status"], "accepted")
        self.assertEqual(len(self.service.feedback_log), 1)
        self.assertEqual(self.service.feedback_log[0]["issueType"], "RECOMMENDED_TOO_SMALL")

    def test_native_mobile_view_renderer_surface1(self):
        confidence_data = self.service.get_fit_confidence("style_3948102", "usr_98745210")
        chip = self.renderer.render_surface1_wishlist_fit_chip(confidence_data)
        self.assertEqual(chip["componentType"], "ConfidenceStatusBadge")
        self.assertTrue(chip["showSizeChip"])
        self.assertEqual(chip["chipText"], "Rec. Size: M (88% match)")

    def test_native_mobile_view_renderer_surface2(self):
        confidence_data = self.service.get_fit_confidence("style_3948102", "usr_98745210")
        sheet = self.renderer.render_surface2_fit_detail_sheet(confidence_data)
        self.assertEqual(sheet["surfaceId"], "FitConfidenceDetailSheet")
        self.assertFalse(sheet["isFallback"])
        self.assertEqual(len(sheet["widgets"]), 5)

if __name__ == "__main__":
    unittest.main()
