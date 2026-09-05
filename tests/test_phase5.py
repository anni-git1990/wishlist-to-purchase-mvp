"""
Unit and Integration Test Suite for Phase 5 Deliverables (Decision Trigger Layer)
Tests:
1. FrequencyCapService Redis Global & Item-Level Frequency Caps.
2. Quiet Hours (22:00-08:00) Timezone Enforcement.
3. Zero Monetary Policy Banned Keyword Guardrail.
4. Already Purchased / Removed Wishlist Item Suppression.
5. NotificationGatewayService APNs (iOS) & FCM (Android) Deep Link Generation.
6. TriggerEvaluationService End-to-End Execution.
"""

import sys
import os
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.frequency_cap_service import FrequencyCapService
from services.notification_gateway_service import NotificationGatewayService
from services.trigger_evaluation_service import TriggerEvaluationService


class TestPhase5Deliverables(unittest.TestCase):

    def setUp(self):
        self.freq_cap = FrequencyCapService(global_user_cap_per_week=2, item_cap_days=14)
        self.gateway = NotificationGatewayService()
        self.evaluator = TriggerEvaluationService(self.freq_cap, self.gateway)

    def test_zero_monetary_policy_rejection(self):
        valid_msg = "3 buyers with your exact fit left reviews yesterday."
        is_ok, msg = self.freq_cap.evaluate_notification_eligibility("usr_101", "style_01", valid_msg)
        self.assertTrue(is_ok, f"Valid message rejected: {msg}")

        discount_msgs = [
            "Get 20% off on your wishlisted shirt!",
            "Price drop alert! Save Rs. 500 now.",
            "Use coupon WISHLIST20 for discount",
            "Big sale deal available today!"
        ]
        for bad_msg in discount_msgs:
            is_ok, reason = self.freq_cap.evaluate_notification_eligibility("usr_101", "style_01", bad_msg)
            self.assertFalse(is_ok, f"Monetary violation was not blocked: '{bad_msg}'")
            self.assertIn("ZERO_MONETARY_RULE_VIOLATION", reason)

    def test_quiet_hours_enforcement(self):
        msg = "New fit evidence added for your shirt."
        # Daytime 14:00 -> OK
        ok_day, _ = self.freq_cap.evaluate_notification_eligibility("usr_101", "style_01", msg, user_local_hour=14)
        self.assertTrue(ok_day)

        # Quiet hours 23:00 -> Blocked
        ok_night, reason_night = self.freq_cap.evaluate_notification_eligibility("usr_101", "style_01", msg, user_local_hour=23)
        self.assertFalse(ok_night)
        self.assertIn("QUIET_HOURS", reason_night)

    def test_purchased_item_suppression(self):
        msg = "New reviews added for your saved shirt."
        ok_purchased, reason = self.freq_cap.evaluate_notification_eligibility("usr_101", "style_01", msg, wishlist_item_status="PURCHASED")
        self.assertFalse(ok_purchased)
        self.assertIn("PURCHASED", reason)

    def test_global_user_frequency_cap(self):
        msg1 = "Update 1: New review added."
        msg2 = "Update 2: Recommended size back in stock."
        msg3 = "Update 3: Low inventory alert."

        # Dispatch 1 -> Eligible
        ok1, _ = self.freq_cap.evaluate_notification_eligibility("usr_cap_01", "style_01", msg1)
        self.assertTrue(ok1)
        self.freq_cap.record_notification_sent("usr_cap_01", "style_01")

        # Dispatch 2 (different item) -> Eligible
        ok2, _ = self.freq_cap.evaluate_notification_eligibility("usr_cap_01", "style_02", msg2)
        self.assertTrue(ok2)
        self.freq_cap.record_notification_sent("usr_cap_01", "style_02")

        # Dispatch 3 -> Should be blocked by Global Cap (Max 2/week)
        ok3, reason3 = self.freq_cap.evaluate_notification_eligibility("usr_cap_01", "style_03", msg3)
        self.assertFalse(ok3)
        self.assertIn("GLOBAL_USER_FREQUENCY_CAP", reason3)

    def test_notification_gateway_deep_links(self):
        # iOS APNs
        res_ios = self.gateway.dispatch_notification("usr_101", "iOS", "NEW_FIT_EVIDENCE", "style_3948102", "3 reviews added.")
        self.assertEqual(res_ios["status"], "success")
        self.assertEqual(res_ios["gateway"], "APNs")
        self.assertIn("myntra://wishlist/detail?productId=style_3948102&sheet=fit", res_ios["payload"]["uriScheme"])

        # Android FCM
        res_fcm = self.gateway.dispatch_notification("usr_102", "Android", "NEW_FIT_EVIDENCE", "style_3948102", "3 reviews added.")
        self.assertEqual(res_fcm["gateway"], "FCM")
        self.assertIn("myntra://wishlist/detail?productId=style_3948102&sheet=fit", res_fcm["payload"]["data"]["uriScheme"])

    def test_trigger_evaluation_service_end_to_end(self):
        res = self.evaluator.evaluate_trigger_event({
            "productId": "style_3948102",
            "triggerEventType": "NEW_FIT_EVIDENCE",
            "minNewReviews": 3
        })
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["usersEvaluated"], 4)
        self.assertGreater(res["notificationsQueued"], 0)
        self.assertIn("suppressedSummary", res)

if __name__ == "__main__":
    unittest.main()
