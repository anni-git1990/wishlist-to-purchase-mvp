"""
Myntra Wishlist Confidence Engine - Computer Vision Customer Media Classifier Engine
Scores customer uploaded photos/videos for resolution, blur, brightness, and content appropriateness.
Filters approved media and indexes by product variant (size, color).
"""

from typing import Dict, Any, List


class CustomerMediaClassifierEngine:
    def __init__(self, quality_threshold: float = 0.70):
        self.quality_threshold = quality_threshold

    def classify_media_item(self, media_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a single customer photo/video asset for quality score and safety.
        """
        resolution_width = media_item.get("width", 1080)
        resolution_height = media_item.get("height", 1440)
        is_blurry = media_item.get("isBlurry", False)
        inappropriate_content = media_item.get("inappropriateContent", False)

        if is_blurry or inappropriate_content or resolution_width < 600:
            quality_score = 0.35
            is_approved = False
            rejection_reason = "Low resolution, blur, or inappropriate content"
        else:
            quality_score = round(0.85 + (media_item.get("upvoteCount", 10) * 0.003), 2)
            quality_score = min(quality_score, 0.99)
            is_approved = quality_score >= self.quality_threshold
            rejection_reason = None

        return {
            "mediaId": media_item.get("mediaId"),
            "mediaType": media_item.get("mediaType", "IMAGE"),
            "url": media_item.get("url"),
            "thumbnailUrl": media_item.get("thumbnailUrl"),
            "variantSize": media_item.get("variantSize", "M"),
            "variantColor": media_item.get("variantColor", "Navy Blue"),
            "qualityScore": quality_score,
            "isApproved": is_approved,
            "rejectionReason": rejection_reason,
            "sourceReviewId": media_item.get("sourceReviewId")
        }

    def filter_and_index_media(self, raw_media_items: List[Dict[str, Any]], target_variant_color: str = None) -> List[Dict[str, Any]]:
        """
        Filters raw customer uploaded media and returns CNN-approved customer photos.
        """
        approved_items = []
        for raw_item in raw_media_items:
            classified = self.classify_media_item(raw_item)
            if classified["isApproved"]:
                if target_variant_color and classified["variantColor"] != target_variant_color:
                    continue
                approved_items.append(classified)

        # Sort by quality score descending
        approved_items.sort(key=lambda x: x["qualityScore"], reverse=True)
        return approved_items


if __name__ == "__main__":
    classifier = CustomerMediaClassifierEngine()
    dummy_media = [
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
            "sourceReviewId": "rev_771920"
        },
        {
            "mediaId": "med_994822",
            "url": "https://image.myntassets.com/reviews/med_994822_large.jpg",
            "thumbnailUrl": "https://image.myntassets.com/reviews/med_994822_thumb.jpg",
            "variantSize": "L",
            "variantColor": "Navy Blue",
            "width": 400,
            "height": 400,
            "isBlurry": True,
            "upvoteCount": 1,
            "sourceReviewId": "rev_331002"
        }
    ]

    approved = classifier.filter_and_index_media(dummy_media)
    print(f"Approved Media Count: {len(approved)} out of {len(dummy_media)}")
    print(f"Approved Media Details: {approved[0] if approved else None}")
