"""
Myntra Wishlist Confidence Engine - Native Mobile Quality Digest UI Component Renderer (iOS & Android)
Defines UI view model structures, aspect sentiment cards, and customer photo carousel components for Surface 1 & Surface 3.
"""

from typing import Dict, Any, List


class NativeMobileQualityViewRenderer:
    """
    Renders UI component view models for Native iOS (SwiftUI) & Native Android (Jetpack Compose) Quality Digest.
    """

    @staticmethod
    def render_surface1_quality_summary_snippet(quality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renders Surface 1 inline 1-line Quality Summary Snippet on mobile wishlist item cards.
        """
        data = quality_data.get("data", {})
        threshold_met = data.get("reviewThresholdMet", False)
        preview_text = data.get("summaryPreview", "Quality reviews available.")

        if not threshold_met:
            return {
                "componentType": "QualitySummarySnippet",
                "showSnippet": False,
                "displayText": "Insufficient review evidence",
                "ctaAction": "VIEW_STANDARD_REVIEWS"
            }

        return {
            "componentType": "QualitySummarySnippet",
            "showSnippet": True,
            "displayText": preview_text,
            "overallScore": data.get("overallQualityScore", 4.4),
            "mediaCount": len(data.get("verifiedCustomerMedia", [])),
            "ctaAction": "OPEN_QUALITY_DETAIL_SHEET"
        }

    @staticmethod
    def render_surface3_quality_detail_sheet(quality_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renders Surface 3 Review and Quality Detail Bottom Sheet view structure.
        """
        data = quality_data.get("data", {})
        aspects = data.get("aspectSummaries", [])
        media_list = data.get("verifiedCustomerMedia", [])
        scorecard = data.get("durabilityScorecard", {})

        return {
            "surfaceId": "ReviewAndQualityDetailSheet",
            "title": "Review & Quality Digest",
            "widgets": [
                {
                    "widgetType": "OverallQualityScorecard",
                    "ratingScore": data.get("overallQualityScore", 4.4),
                    "totalReviewsAnalyzed": data.get("totalReviewsAnalyzed", 0),
                    "durabilityScorecard": scorecard
                },
                {
                    "widgetType": "AspectSentimentGrid",
                    "aspectCards": [
                        {
                            "aspectName": a.get("aspectName"),
                            "sentiment": a.get("sentiment"),
                            "summaryText": a.get("summaryText"),
                            "supportingReviewCount": len(a.get("supportingReviews", [])),
                            "supportingReviewIds": a.get("supportingReviews", [])
                        } for a in aspects
                    ]
                },
                {
                    "widgetType": "VerifiedMediaCarousel",
                    "header": "Verified Customer Photos & Videos",
                    "supportsZoom": True,
                    "supportsVariantFilter": True,
                    "mediaCount": len(media_list),
                    "items": [
                        {
                            "mediaId": m.get("mediaId"),
                            "url": m.get("url"),
                            "thumbnailUrl": m.get("thumbnailUrl"),
                            "variantSize": m.get("variantSize"),
                            "variantColor": m.get("variantColor"),
                            "sourceReviewId": m.get("sourceReviewId")
                        } for m in media_list
                    ]
                },
                {
                    "widgetType": "SourceReviewLink",
                    "buttonText": f"View All {data.get('totalReviewsAnalyzed', 0)} Verified Reviews",
                    "anchorUrl": f"myntra://reviews/list?productId={data.get('productId')}"
                }
            ]
        }


if __name__ == "__main__":
    from services.quality_digest_service import QualityDigestService
    svc = QualityDigestService()
    data = svc.get_quality_digest("style_3948102")
    
    renderer = NativeMobileQualityViewRenderer()
    snippet = renderer.render_surface1_quality_summary_snippet(data)
    sheet = renderer.render_surface3_quality_detail_sheet(data)

    print("Surface 1 Quality Snippet:", snippet)
    print("Surface 3 Detail Sheet Widget Count:", len(sheet["widgets"]))
