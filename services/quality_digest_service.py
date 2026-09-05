"""
Myntra Wishlist Confidence Engine - Quality Digest Microservice
Serves GET /api/v1/products/{productId}/quality-digest with Redis caching,
and handles review deletion cache invalidation hooks.
"""

import time
from typing import Dict, Any, Optional, List
from ml_services.review_summarizer_engine import ReviewSummarizerEngine
from ml_services.media_classifier_engine import CustomerMediaClassifierEngine
from services.cache_service import CacheService


class QualityDigestService:
    def __init__(self, cache_service: Optional[CacheService] = None):
        self.summarizer = ReviewSummarizerEngine()
        self.media_classifier = CustomerMediaClassifierEngine()
        self.cache = cache_service if cache_service else CacheService()

    def get_quality_digest(self, product_id: str, variant_color: Optional[str] = None, mock_low_reviews: bool = False) -> Dict[str, Any]:
        """
        Fetches quality digest and verified customer media for a product.
        """
        start_time = time.time()
        cache_key = f"quality_digest:{product_id}:{variant_color or 'all'}:{mock_low_reviews}"

        # 1. Cache Lookup
        cached_result = self.cache.get(cache_key)
        if cached_result:
            cached_result["latencyMs"] = round((time.time() - start_time) * 1000, 2)
            cached_result["fromCache"] = True
            return cached_result

        # 2. Fetch Raw Reviews Data (Simulated Database Query with 12 reviews >= 10 threshold)
        if mock_low_reviews:
            raw_reviews = [
                {"reviewId": "rev_771920", "text": "100% cotton shirt, fits great", "rating": 5},
                {"reviewId": "rev_881203", "text": "Soft fabric and good stitching", "rating": 4}
            ]
        else:
            raw_reviews = [
                {"reviewId": f"rev_{100 + i}", "text": "High quality fabric and fit", "rating": 4 + (i % 2)}
                for i in range(12)
            ]

        raw_media = [
            {
                "mediaId": "med_994821",
                "url": "https://image.myntassets.com/reviews/med_994821_large.jpg",
                "thumbnailUrl": "https://image.myntassets.com/reviews/med_994821_thumb.jpg",
                "variantSize": "M",
                "variantColor": "Navy Blue",
                "width": 1080,
                "height": 1440,
                "isBlurry": False,
                "upvoteCount": 34,
                "sourceReviewId": "rev_100"
            }
        ]

        # 3. Generate Digest & Classify Media
        digest = self.summarizer.generate_quality_digest(product_id, raw_reviews)
        approved_media = self.media_classifier.filter_and_index_media(raw_media, target_variant_color=variant_color)

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        response = {
            "status": "success",
            "data": {
                "productId": product_id,
                "summaryVersion": digest.get("summaryVersion", 1.4),
                "reviewThresholdMet": digest.get("reviewThresholdMet", True),
                "totalReviewsAnalyzed": digest.get("totalReviewsAnalyzed", len(raw_reviews)),
                "overallQualityScore": digest.get("overallQualityScore", 4.4),
                "summaryPreview": digest.get("summaryPreview"),
                "topPositiveAspect": digest.get("topPositiveAspect"),
                "topNegativeAspect": digest.get("topNegativeAspect"),
                "aspectSummaries": digest.get("aspects", []),
                "verifiedCustomerMedia": approved_media,
                "durabilityScorecard": {
                    "stitchQuality": 4.5,
                    "fabricWeight": "180 GSM (Heavyweight Cotton)",
                    "colorFidelity": 4.6
                },
                "lastUpdated": digest.get("updatedAt")
            },
            "latencyMs": elapsed_ms,
            "fromCache": False,
            "slaMet": elapsed_ms < 50.0
        }

        # Cache for 1 hour
        self.cache.set(cache_key, response, ttl_seconds=3600)
        return response

    def handle_review_deleted_event(self, review_id: str, product_id: str) -> int:
        """
        Kafka Event Handler for `review_deleted`. Purges cached quality digest keys.
        """
        prefix = f"quality_digest:{product_id}"
        purged_count = self.cache.invalidate_prefix(prefix)
        print(f"[Review Deleted Consumer] Invalidated {purged_count} cache keys for product '{product_id}' due to deletion of '{review_id}'.")
        return purged_count


if __name__ == "__main__":
    svc = QualityDigestService()
    res = svc.get_quality_digest("style_3948102")
    print(f"Quality Digest Response (Latency: {res['latencyMs']}ms):")
    print(f"  • Preview: {res['data']['summaryPreview']}")
    print(f"  • Media Count: {len(res['data']['verifiedCustomerMedia'])}")

    # Test cache invalidation on review deletion
    purged = svc.handle_review_deleted_event("rev_771920", "style_3948102")
    print(f"Purged Keys: {purged}")
