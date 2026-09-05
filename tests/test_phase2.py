"""
Unit and Integration Test Suite for Phase 2 Deliverables
Tests:
1. A/B Assignment MurmurHash3 Randomization & Balance Check.
2. CacheService TTL, Invalidation, and Hit Rate Telemetry.
3. FeatureStoreService Feature Vector Retrieval & Updates.
4. EventIngestionService Ingestion & Real-Time Flink Attribution.
5. Surface 4 Internal Admin Dashboard Backend Specs.
"""

import sys
import os
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.ab_assignment_service import ABAssignmentService, CONTROL_GROUP, TREATMENT_GROUP
from services.cache_service import CacheService
from services.feature_store_service import FeatureStoreService
from services.event_ingestion_service import EventIngestionService
from dashboard.app import DashboardMetricsBackend


class TestPhase2Deliverables(unittest.TestCase):

    def test_ab_assignment_deterministic_and_balanced(self):
        service = ABAssignmentService()
        
        # Test deterministic output
        res1 = service.get_assignment("usr_98745210")
        res2 = service.get_assignment("usr_98745210")
        self.assertEqual(res1["experimentGroup"], res2["experimentGroup"])
        self.assertEqual(res1["bucket"], res2["bucket"])

        # Test balance across 10,000 synthetic users
        synthetic_uids = [f"usr_test_{i}" for i in range(10000)]
        audit = service.verify_no_leakage(synthetic_uids)
        self.assertEqual(audit["totalEvaluated"], 10000)
        self.assertTrue(audit["isBalanced"], f"Treatment % out of range: {audit['treatmentPercentage']}%")

    def test_cache_service_operations_and_stats(self):
        cache = CacheService(default_ttl_seconds=3600)
        
        # Test set & get
        cache.set("confidence:user:101", {"recSize": "M"})
        val = cache.get("confidence:user:101")
        self.assertIsNotNone(val)
        self.assertEqual(val["recSize"], "M")

        # Test miss
        miss_val = cache.get("confidence:user:nonexistent")
        self.assertIsNone(miss_val)

        # Test invalidation
        cache.invalidate("confidence:user:101")
        self.assertIsNone(cache.get("confidence:user:101"))

        # Test stats
        stats = cache.get_stats()
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 2)

    def test_feature_store_service(self):
        fs = FeatureStoreService()
        
        # Test known user vector
        vec = fs.get_user_fit_vector("usr_98745210")
        self.assertEqual(vec["height_cm"], 178)
        self.assertTrue(vec["consent_given"])

        # Test cold start user vector fallback
        cold_vec = fs.get_user_fit_vector("usr_cold_001")
        self.assertIsNone(cold_vec["height_cm"])
        self.assertFalse(cold_vec["consent_given"])

    def test_event_ingestion_and_flink_attribution(self):
        ingestion = EventIngestionService()

        # Ingest Wishlist Add Events
        ingestion.ingest_event({
            "eventId": "evt_101",
            "eventName": "wishlist_item_added",
            "timestamp": "2026-09-04T15:00:00Z",
            "userId": "usr_treatment_01",
            "productId": "style_3948102",
            "variantId": "sku_991823",
            "sourceSurface": "PDP",
            "experimentGroup": TREATMENT_GROUP
        })

        ingestion.ingest_event({
            "eventId": "evt_102",
            "eventName": "wishlist_item_added",
            "timestamp": "2026-09-04T15:00:00Z",
            "userId": "usr_control_01",
            "productId": "style_3948102",
            "variantId": "sku_991823",
            "sourceSurface": "PDP",
            "experimentGroup": CONTROL_GROUP
        })

        # Ingest Purchase Events
        ingestion.ingest_event({
            "eventId": "evt_103",
            "eventName": "wishlisted_item_purchased",
            "timestamp": "2026-09-05T10:00:00Z",
            "userId": "usr_treatment_01",
            "orderId": "ord_9901",
            "productId": "style_3948102",
            "daysSinceWishlistAdd": 1,
            "wasPurchasedWithin30Days": True,
            "experimentGroup": TREATMENT_GROUP
        })

        attribution = ingestion.get_attribution_summary()
        self.assertEqual(attribution["treatment"]["wishlistAdders"], 1)
        self.assertEqual(attribution["treatment"]["purchasers30d"], 1)
        self.assertEqual(attribution["treatment"]["conversionRate"], 1.0)
        self.assertEqual(attribution["control"]["wishlistAdders"], 1)
        self.assertEqual(attribution["control"]["purchasers30d"], 0)
        self.assertEqual(attribution["control"]["conversionRate"], 0.0)

    def test_dashboard_backend_metrics(self):
        backend = DashboardMetricsBackend()
        data = backend.get_dashboard_summary()
        self.assertIn("experiment", data)
        self.assertIn("conversionFunnel", data)
        self.assertIn("mlModelQuality", data)
        self.assertIn("guardrails", data)
        self.assertGreaterEqual(len(data["guardrails"]), 3)

if __name__ == "__main__":
    unittest.main()
