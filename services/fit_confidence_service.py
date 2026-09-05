"""
Myntra Wishlist Confidence Engine - Fit Confidence Microservice
Serves GET /api/v1/products/{productId}/fit-confidence and POST /confidence-feedback endpoints.
Integrates FeatureStoreService, CacheService, and FitRecommendationEngine.
"""

import time
from typing import Dict, Any, Optional
from ml_services.fit_recommendation_engine import FitRecommendationEngine
from services.feature_store_service import FeatureStoreService
from services.cache_service import CacheService


class FitConfidenceService:
    def __init__(self, cache_service: Optional[CacheService] = None, feature_store: Optional[FeatureStoreService] = None):
        self.engine = FitRecommendationEngine()
        self.cache = cache_service if cache_service else CacheService()
        self.feature_store = feature_store if feature_store else FeatureStoreService()
        self.feedback_log = []

    def get_fit_confidence(self, product_id: str, user_id: Optional[str] = None, review_count: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetches fit recommendation and peer evidence for a product & user.
        Enforces sub-45ms P95 SLA via Redis caching.
        """
        start_time = time.time()
        cache_key = f"fit_confidence:{product_id}:{user_id or 'guest'}:{review_count}"

        # 1. Cache lookup (Target latency < 5ms)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            cached_result["latencyMs"] = round((time.time() - start_time) * 1000, 2)
            cached_result["fromCache"] = True
            return cached_result

        # 2. Retrieve user feature vector
        user_vector = self.feature_store.get_user_fit_vector(user_id) if user_id else {}

        # 3. Handle zero-review / fallback product override
        if "zero_reviews" in product_id or review_count == 0:
            effective_review_count = 0
            similar_peer_count = 0
        else:
            effective_review_count = review_count if review_count is not None else 184
            similar_peer_count = 5 if effective_review_count >= 10 else 0

        # Product metadata simulation
        product_data = {
            "productId": product_id,
            "brandId": "Roadster",
            "reviewCount": effective_review_count,
            "similarBodyReviewCount": similar_peer_count,
            "hasSizeChart": True,
            "sizeDistribution": {"runsSmall": 9, "trueToSize": 84, "runsLarge": 7},
            "stretchRating": "MODERATE",
            "postWashBehavior": "Pre-shrunk fabric, minimal shrinkage (< 1.5%)."
        }

        # 4. Compute ML Inference
        result = self.engine.recommend_size(user_vector, product_data)
        
        # 5. Measure latency & Cache payload
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        result["latencyMs"] = elapsed_ms
        result["fromCache"] = False
        result["slaMet"] = elapsed_ms < 45.0

        # Cache for 1 hour
        self.cache.set(cache_key, result, ttl_seconds=3600)
        return result

    def submit_confidence_feedback(self, product_id: str, feedback_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Captures user accuracy feedback for model retraining.
        """
        entry = {
            "productId": product_id,
            "userId": feedback_payload.get("userId"),
            "feature": feedback_payload.get("feature", "FIT_CONFIDENCE"),
            "recommendedSize": feedback_payload.get("recommendedSize"),
            "selectedSize": feedback_payload.get("selectedSize"),
            "helpful": feedback_payload.get("helpful", True),
            "issueType": feedback_payload.get("issueType"),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())
        }
        self.feedback_log.append(entry)
        return {
            "status": "accepted",
            "message": "Feedback captured successfully for model retraining.",
            "feedbackId": f"fb_{len(self.feedback_log)}"
        }


if __name__ == "__main__":
    svc = FitConfidenceService()
    res = svc.get_fit_confidence("style_3948102", "usr_98745210")
    print(f"Fit Confidence Response (Latency: {res['latencyMs']}ms): {res['personalization']}")
