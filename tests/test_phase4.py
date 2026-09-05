"""
Unit and Integration Test Suite for Phase 4 Deliverables (Review & Quality Digest MVP)
Tests:
1. ReviewSummarizerEngine ABSA Aspect Sentiment Extraction & Traceability Pointer Guardrail.
2. CustomerMediaClassifierEngine CNN Quality Scoring & Variant Filtering.
3. QualityDigestService Endpoint Latency SLA (<50ms), Redis Caching & Review Deletion Cache Invalidation.
4. Native Mobile UI View Model Renderer for Surface 1 Preview Snippets & Surface 3 Detail Sheets.
"""

import sys
import os
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml_services.review_summarizer_engine import ReviewSummarizerEngine
from ml_services.media_classifier_engine import CustomerMediaClassifierEngine
from services.quality_digest_service import QualityDigestService
from mobile_views.quality_digest_views import NativeMobileQualityViewRenderer


class TestPhase4Deliverables(unittest.TestCase):

    def setUp(self):
        self.summarizer = ReviewSummarizerEngine()
        self.classifier = CustomerMediaClassifierEngine()
        self.service = QualityDigestService()
        self.renderer = NativeMobileQualityViewRenderer()

    def test_review_summarizer_engine_traceability(self):
        raw_reviews = [
            {"reviewId": "rev_771920", "text": "100% cotton shirt, fits great", "rating": 5},
            {"reviewId": "rev_881203", "text": "Soft fabric and good stitching", "rating": 4},
            {"reviewId": "rev_991024", "text": "Breathable material for summer", "rating": 5},
            {"reviewId": "rev_551029", "text": "No shrinkage after cold wash", "rating": 4},
            {"reviewId": "rev_663110", "text": "Color matches image", "rating": 4},
            {"reviewId": "rev_331002", "text": "Small thread on sleeve cuff", "rating": 3}
        ]

        digest = self.summarizer.generate_quality_digest("style_3948102", raw_reviews)
        self.assertEqual(digest["productId"], "style_3948102")
        self.assertGreater(len(digest["aspects"]), 0)
        
        # Verify 100% traceability pointers
        source_ids = {r["reviewId"] for r in raw_reviews}
        for aspect in digest["aspects"]:
            for ptr in aspect["supportingReviews"]:
                self.assertIn(ptr, source_ids, f"Traceability failed: {ptr} not in source reviews")

    def test_customer_media_classifier_engine(self):
        dummy_media = [
            {
                "mediaId": "med_good_01",
                "url": "https://image.myntassets.com/good.jpg",
                "thumbnailUrl": "https://image.myntassets.com/thumb.jpg",
                "variantSize": "M",
                "variantColor": "Navy Blue",
                "width": 1080,
                "height": 1440,
                "isBlurry": False,
                "upvoteCount": 20,
                "sourceReviewId": "rev_771920"
            },
            {
                "mediaId": "med_bad_01",
                "url": "https://image.myntassets.com/bad.jpg",
                "thumbnailUrl": "https://image.myntassets.com/thumb_bad.jpg",
                "variantSize": "M",
                "variantColor": "Navy Blue",
                "width": 400,
                "height": 400,
                "isBlurry": True,
                "upvoteCount": 0,
                "sourceReviewId": "rev_331002"
            }
        ]

        approved = self.classifier.filter_and_index_media(dummy_media)
        self.assertEqual(len(approved), 1)
        self.assertEqual(approved[0]["mediaId"], "med_good_01")
        self.assertTrue(approved[0]["isApproved"])

    def test_quality_digest_service_latency_and_cache_invalidation(self):
        # Cold call
        res1 = self.service.get_quality_digest("style_3948102")
        self.assertEqual(res1["status"], "success")
        self.assertTrue(res1["slaMet"], f"Latency {res1['latencyMs']}ms exceeded 50ms SLA")
        self.assertFalse(res1["fromCache"])

        # Hot cache call
        res2 = self.service.get_quality_digest("style_3948102")
        self.assertTrue(res2["fromCache"])
        self.assertLess(res2["latencyMs"], 15.0)

        # Test Kafka review_deleted cache invalidation hook
        purged_count = self.service.handle_review_deleted_event("rev_771920", "style_3948102")
        self.assertGreater(purged_count, 0)

        # Next call should be cache miss
        res3 = self.service.get_quality_digest("style_3948102")
        self.assertFalse(res3["fromCache"])

    def test_native_mobile_quality_view_renderer(self):
        data = self.service.get_quality_digest("style_3948102")
        
        # Test Surface 1 snippet (threshold met >= 10 reviews)
        snippet = self.renderer.render_surface1_quality_summary_snippet(data)
        self.assertEqual(snippet["componentType"], "QualitySummarySnippet")
        self.assertTrue(snippet["showSnippet"])

        # Test Surface 1 snippet (threshold NOT met < 10 reviews)
        low_data = self.service.get_quality_digest("style_low_01", mock_low_reviews=True)
        low_snippet = self.renderer.render_surface1_quality_summary_snippet(low_data)
        self.assertFalse(low_snippet["showSnippet"])

        # Test Surface 3 detail sheet
        sheet = self.renderer.render_surface3_quality_detail_sheet(data)
        self.assertEqual(sheet["surfaceId"], "ReviewAndQualityDetailSheet")
        self.assertEqual(len(sheet["widgets"]), 4)

if __name__ == "__main__":
    unittest.main()
