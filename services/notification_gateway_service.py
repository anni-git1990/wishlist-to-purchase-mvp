"""
Myntra Wishlist Confidence Engine - APNs / FCM Push Notification & Deep-Link Gateway
Dispatches push notification payloads for iOS (APNs) & Android (FCM),
and constructs Universal Links / App Links pointing to native detail sheets.
"""

import time
from typing import Dict, Any, Optional


class NotificationGatewayService:
    def __init__(self):
        self.dispatched_logs: List[Dict[str, Any]] = []

    def build_deep_link(self, product_id: str, trigger_type: str) -> Dict[str, str]:
        """
        Constructs Universal Links (iOS) & App Links (Android) for deep-linking into native mobile views.
        """
        sheet_param = "fit"
        if trigger_type == "NEW_FIT_EVIDENCE":
            sheet_param = "fit"
        elif trigger_type == "QUALITY_UPDATE":
            sheet_param = "quality"
        elif trigger_type == "SIZE_BACK_IN_STOCK":
            sheet_param = "fit"

        uri_scheme = f"myntra://wishlist/detail?productId={product_id}&sheet={sheet_param}&source=notification"
        universal_link = f"https://www.myntra.com/wishlist/detail?productId={product_id}&sheet={sheet_param}"

        return {
            "uriScheme": uri_scheme,
            "universalLink": universal_link
        }

    def dispatch_notification(
        self,
        user_id: str,
        platform: str,
        trigger_type: str,
        product_id: str,
        message_text: str
    ) -> Dict[str, Any]:
        """
        Constructs APNs or FCM push notification payload and dispatches to mobile gateways.
        """
        links = self.build_deep_link(product_id, trigger_type)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())
        notification_id = f"notif_{int(time.time() * 1000)}"

        if platform.upper() == "IOS":
            payload = {
                "aps": {
                    "alert": {
                        "title": "Wishlist Evidence Update",
                        "body": message_text
                    },
                    "sound": "default",
                    "badge": 1,
                    "category": "WISHLIST_CONFIDENCE_UPDATE"
                },
                "deepLink": links["universalLink"],
                "uriScheme": links["uriScheme"],
                "notificationId": notification_id,
                "productId": product_id,
                "triggerType": trigger_type
            }
            gateway = "APNs"
        else:  # Android (FCM)
            payload = {
                "notification": {
                    "title": "Wishlist Evidence Update",
                    "body": message_text
                },
                "data": {
                    "deepLink": links["universalLink"],
                    "uriScheme": links["uriScheme"],
                    "notificationId": notification_id,
                    "productId": product_id,
                    "triggerType": trigger_type
                },
                "priority": "high"
            }
            gateway = "FCM"

        log_entry = {
            "notificationId": notification_id,
            "userId": user_id,
            "platform": platform.upper(),
            "gateway": gateway,
            "triggerType": trigger_type,
            "productId": product_id,
            "message": message_text,
            "deepLink": links["universalLink"],
            "dispatchedAt": timestamp,
            "status": "DELIVERED"
        }
        self.dispatched_logs.append(log_entry)

        return {
            "status": "success",
            "gateway": gateway,
            "notificationId": notification_id,
            "payload": payload,
            "dispatchedAt": timestamp
        }


if __name__ == "__main__":
    gateway = NotificationGatewayService()
    res_ios = gateway.dispatch_notification(
        user_id="usr_101",
        platform="iOS",
        trigger_type="NEW_FIT_EVIDENCE",
        product_id="style_3948102",
        message_text="3 buyers with your exact fit left reviews yesterday."
    )
    print("iOS APNs Dispatch:", res_ios["gateway"], res_ios["status"])
    print("Deep Link URI:", res_ios["payload"]["uriScheme"])
