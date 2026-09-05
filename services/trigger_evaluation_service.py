"""
Myntra Wishlist Confidence Engine - Real-Time Trigger Evaluation Microservice
Serves POST /api/v1/wishlist/triggers/evaluate. Evaluates candidate triggers against
FrequencyCapService rules and dispatches approved push notifications via NotificationGatewayService.
"""

from typing import Dict, Any, List, Optional
from services.frequency_cap_service import FrequencyCapService
from services.notification_gateway_service import NotificationGatewayService


class TriggerEvaluationService:
    def __init__(self, frequency_cap_service: Optional[FrequencyCapService] = None, gateway_service: Optional[NotificationGatewayService] = None):
        self.freq_cap = frequency_cap_service if frequency_cap_service else FrequencyCapService()
        self.gateway = gateway_service if gateway_service else NotificationGatewayService()

    def evaluate_trigger_event(self, trigger_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates candidate event (e.g. inventory restock or new peer reviews) across candidate wishlist users.
        """
        product_id = trigger_event.get("productId")
        trigger_type = trigger_event.get("triggerEventType", "NEW_FIT_EVIDENCE")
        min_reviews = trigger_event.get("minNewReviews", 3)

        # Simulated Wishlist Users watching this product
        candidate_users = [
            {"userId": "usr_101", "platform": "iOS", "wishlistStatus": "ACTIVE", "localHour": 14},
            {"userId": "usr_102", "platform": "Android", "wishlistStatus": "ACTIVE", "localHour": 23},  # Quiet hours
            {"userId": "usr_103", "platform": "iOS", "wishlistStatus": "PURCHASED", "localHour": 15},  # Already bought
            {"userId": "usr_104", "platform": "Android", "wishlistStatus": "ACTIVE", "localHour": 11}
        ]

        if trigger_type == "NEW_FIT_EVIDENCE":
            message_text = f"{min_reviews} buyers with your exact fit profile left reviews yesterday."
        elif trigger_type == "SIZE_BACK_IN_STOCK":
            message_text = "Your recommended size is back in stock! Stock is limited."
        elif trigger_type == "LOW_INVENTORY_ALERT":
            message_text = "Only 2 items left in your recommended size!"
        else:
            message_text = "Your saved wishlist item has a new evidence update."

        evaluated_count = len(candidate_users)
        queued_count = 0
        suppressed_summary: Dict[str, int] = {}

        for user in candidate_users:
            uid = user["userId"]
            platform = user["platform"]
            status = user["wishlistStatus"]
            local_hour = user["localHour"]

            is_eligible, reason = self.freq_cap.evaluate_notification_eligibility(
                user_id=uid,
                product_id=product_id,
                message_text=message_text,
                wishlist_item_status=status,
                user_local_hour=local_hour
            )

            if is_eligible:
                # Dispatch Push Notification
                self.gateway.dispatch_notification(
                    user_id=uid,
                    platform=platform,
                    trigger_type=trigger_type,
                    product_id=product_id,
                    message_text=message_text
                )
                self.freq_cap.record_notification_sent(uid, product_id)
                queued_count += 1
            else:
                suppressed_summary[reason] = suppressed_summary.get(reason, 0) + 1

        return {
            "status": "success",
            "productId": product_id,
            "triggerType": trigger_type,
            "usersEvaluated": evaluated_count,
            "notificationsQueued": queued_count,
            "suppressedSummary": suppressed_summary
        }


if __name__ == "__main__":
    evaluator = TriggerEvaluationService()
    res = evaluator.evaluate_trigger_event({
        "productId": "style_3948102",
        "triggerEventType": "NEW_FIT_EVIDENCE",
        "evidenceThresholdMet": True,
        "minNewReviews": 3
    })
    print(f"Trigger Evaluation Result: Queued {res['notificationsQueued']} of {res['usersEvaluated']} candidates.")
    print("Suppression Reasons Summary:", res["suppressedSummary"])
