"""
Myntra Wishlist Confidence Engine - Native Mobile UI Component Renderer (iOS & Android)
Defines UI view model structures, component states, and native view specifications for Surface 1 & Surface 2.
"""

from typing import Dict, Any, List


class NativeMobileFitViewRenderer:
    """
    Renders UI component view models for Native iOS (SwiftUI) & Native Android (Jetpack Compose).
    """

    @staticmethod
    def render_surface1_wishlist_fit_chip(confidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renders Surface 1 inline Wishlist Fit Status Badge & Recommended Size Chip.
        """
        personalization = confidence_data.get("personalization", {})
        confidence_level = personalization.get("confidenceLevel", "LIMITED_EVIDENCE")
        rec_size = personalization.get("recommendedSize")
        match_pct = personalization.get("fitMatchPercentage")
        fallback_active = confidence_data.get("fallbackState", {}).get("isFallbackActive", False)

        if fallback_active or not rec_size:
            return {
                "componentType": "ConfidenceStatusBadge",
                "badgeText": "Limited Evidence",
                "badgeColor": "#64748b",  # Slate grey
                "showSizeChip": False,
                "chipText": None,
                "ctaAction": "OPEN_SIZE_CHART"
            }

        color_map = {
            "HIGH": "#166534",     # Emerald Green
            "MEDIUM": "#854d0e",   # Warm Amber
            "LIMITED_EVIDENCE": "#64748b"
        }

        text_map = {
            "HIGH": "High Fit Match",
            "MEDIUM": "Medium Fit Match",
            "LIMITED_EVIDENCE": "Limited Evidence"
        }

        return {
            "componentType": "ConfidenceStatusBadge",
            "badgeText": text_map.get(confidence_level, "Fit Match"),
            "badgeColor": color_map.get(confidence_level, "#166534"),
            "showSizeChip": True,
            "chipText": f"Rec. Size: {rec_size} ({match_pct}% match)",
            "selectedSize": rec_size,
            "ctaAction": "OPEN_FIT_DETAIL_SHEET"
        }

    @staticmethod
    def render_surface2_fit_detail_sheet(confidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renders Surface 2 Fit Confidence Detail Bottom Sheet view structure.
        """
        personalization = confidence_data.get("personalization", {})
        fit_metrics = confidence_data.get("fitMetrics", {})
        peer_reviews = confidence_data.get("peerReviews", [])
        fallback = confidence_data.get("fallbackState", {})

        if fallback.get("isFallbackActive", False):
            return {
                "surfaceId": "FitConfidenceDetailSheet",
                "title": "Size & Fit Guide",
                "isFallback": True,
                "widgets": [
                    {
                        "widgetType": "FallbackMessageWidget",
                        "headline": "Limited Fit Evidence Available",
                        "description": "We don't have enough verified reviews or order history for this item yet.",
                        "brandSizeChartUrl": fallback.get("brandSizeChartUrl")
                    }
                ]
            }

        return {
            "surfaceId": "FitConfidenceDetailSheet",
            "title": "Fit & Sizing Confidence",
            "isFallback": False,
            "widgets": [
                {
                    "widgetType": "PersonalizedSizeWidget",
                    "recommendedSize": personalization.get("recommendedSize"),
                    "fitMatchPercentage": personalization.get("fitMatchPercentage"),
                    "confidenceLevel": personalization.get("confidenceLevel"),
                    "primaryReason": personalization.get("primaryReason"),
                    "alternativeOption": {
                        "size": personalization.get("alternativeSize"),
                        "reason": personalization.get("alternativeReason")
                    }
                },
                {
                    "widgetType": "FitAttributeBars",
                    "fitScale": {
                        "value": "TRUE_TO_SIZE",
                        "distribution": fit_metrics.get("sizeDistribution", {})
                    },
                    "stretchRating": fit_metrics.get("stretchRating", "MODERATE"),
                    "postWashBehavior": fit_metrics.get("postWashBehavior")
                },
                {
                    "widgetType": "PeerEvidenceFeed",
                    "sampleSize": fit_metrics.get("sampleSize", 0),
                    "reviews": peer_reviews
                },
                {
                    "widgetType": "FeedbackActionRow",
                    "prompt": "Was this size recommendation helpful?",
                    "actions": ["YES", "NO"]
                },
                {
                    "widgetType": "QuickAddToBagCTA",
                    "buttonText": f"Add Size {personalization.get('recommendedSize')} to Bag",
                    "selectedSize": personalization.get("recommendedSize")
                }
            ]
        }


if __name__ == "__main__":
    from services.fit_confidence_service import FitConfidenceService
    svc = FitConfidenceService()
    data = svc.get_fit_confidence("style_3948102", "usr_98745210")
    
    renderer = NativeMobileFitViewRenderer()
    chip = renderer.render_surface1_wishlist_fit_chip(data)
    sheet = renderer.render_surface2_fit_detail_sheet(data)

    print("Surface 1 Chip Render:")
    print(chip)
    print("\nSurface 2 Detail Sheet Render (Widget count):", len(sheet["widgets"]))
