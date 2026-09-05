"""
Myntra Wishlist Confidence Engine - Feast / Redis Feature Store Service
Manages user fit features (past size purchases, size return frequency, body attributes) for ML inference.
"""

from typing import Dict, Any, Optional


class FeatureStoreService:
    def __init__(self):
        # Simulated Feature Store database
        self._user_features: Dict[str, Dict[str, Any]] = {
            "usr_98745210": {
                "user_id": "usr_98745210",
                "height_cm": 178,
                "weight_kg": 74,
                "chest_cm": 98,
                "waist_cm": 82,
                "preferred_fit_style": "REGULAR",
                "brand_order_history": {
                    "Roadster": {"M": {"purchased": 4, "returned_size": 0}},
                    "Nike": {"L": {"purchased": 2, "returned_size": 1}}
                },
                "category_return_rate_size": 0.02,
                "consent_given": True
            }
        }

    def get_user_fit_vector(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieves user physical profile & fit feature vector.
        Falls back to empty cold-start vector if user not found.
        """
        if user_id in self._user_features:
            return self._user_features[user_id]
        
        # Cold start fallback vector
        return {
            "user_id": user_id,
            "height_cm": None,
            "weight_kg": None,
            "chest_cm": None,
            "waist_cm": None,
            "preferred_fit_style": "REGULAR",
            "brand_order_history": {},
            "category_return_rate_size": 0.05,
            "consent_given": False
        }

    def update_user_fit_vector(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates user feature vector (e.g., after new purchase or profile update).
        """
        vector = self.get_user_fit_vector(user_id)
        vector.update(updates)
        self._user_features[user_id] = vector
        return vector


if __name__ == "__main__":
    fs = FeatureStoreService()
    vec = fs.get_user_fit_vector("usr_98745210")
    print(f"User Vector: {vec}")
