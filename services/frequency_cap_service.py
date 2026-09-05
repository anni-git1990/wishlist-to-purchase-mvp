"""
Myntra Wishlist Confidence Engine - Anti-Fatigue & Frequency Cap Service
Enforces Redis frequency caps (2/week user max, 1/14-days item max), quiet hours (22:00-08:00),
Zero Monetary Policy (rejects discount keywords), and purchase suppression rules.
"""

import time
import re
from typing import Dict, Any, Tuple, List, Optional


class FrequencyCapService:
    def __init__(self, global_user_cap_per_week: int = 2, item_cap_days: int = 14):
        self.global_user_cap = global_user_cap_per_week
        self.item_cap_seconds = item_cap_days * 86400
        self.week_seconds = 7 * 86400

        # Simulated Redis Ledgers
        self._user_push_timestamps: Dict[str, List[float]] = {}
        self._item_push_timestamps: Dict[str, float] = {}

        # Zero Monetary Policy Banned Keywords (Case-Insensitive Regex)
        self.banned_monetary_keywords = [
            r"\bdiscount\b", r"\boff\b", r"\bsale\b", r"\bprice drop\b",
            r"\bcoupon\b", r"\bcashback\b", r"\bdeal\b", r"\bcheap\b",
            r"\bfree\b", r"\brs\.\b", r"\b\d+%\b"
        ]

    def evaluate_notification_eligibility(
        self,
        user_id: str,
        product_id: str,
        message_text: str,
        wishlist_item_status: str = "ACTIVE",
        user_local_hour: int = 14
    ) -> Tuple[bool, str]:
        """
        Main eligibility evaluator. Returns (is_eligible, reason).
        """
        now = time.time()

        # 1. Purchase & Item Suppression Check
        if wishlist_item_status in ("PURCHASED", "REMOVED", "UNAVAILABLE"):
            return False, f"SUPPRESSED_ITEM_STATUS_{wishlist_item_status}"

        # 2. Zero Monetary Policy Check
        for pattern in self.banned_monetary_keywords:
            if re.search(pattern, message_text, re.IGNORECASE):
                return False, f"SUPPRESSED_ZERO_MONETARY_RULE_VIOLATION: Found '{pattern}' in message"

        # 3. Quiet Hours Check (22:00 to 08:00 Local Time)
        if user_local_hour >= 22 or user_local_hour < 8:
            return False, "SUPPRESSED_QUIET_HOURS_POLICY (22:00 to 08:00)"

        # 4. Item Level Frequency Cap (Max 1 per 14 days)
        item_key = f"{user_id}:{product_id}"
        last_item_push = self._item_push_timestamps.get(item_key, 0)
        if (now - last_item_push) < self.item_cap_seconds:
            return False, "SUPPRESSED_ITEM_LEVEL_FREQUENCY_CAP (Max 1 per 14 days)"

        # 5. Global User Level Frequency Cap (Max 2 per 7 days)
        user_history = self._user_push_timestamps.get(user_id, [])
        recent_pushes = [t for t in user_history if (now - t) < self.week_seconds]
        if len(recent_pushes) >= self.global_user_cap:
            return False, f"SUPPRESSED_GLOBAL_USER_FREQUENCY_CAP (Max {self.global_user_cap} per 7 days)"

        return True, "ELIGIBLE"

    def record_notification_sent(self, user_id: str, product_id: str):
        """
        Records push dispatch in Redis frequency ledger.
        """
        now = time.time()
        
        # Record user push
        if user_id not in self._user_push_timestamps:
            self._user_push_timestamps[user_id] = []
        self._user_push_timestamps[user_id].append(now)

        # Record item push
        item_key = f"{user_id}:{product_id}"
        self._item_push_timestamps[item_key] = now


if __name__ == "__main__":
    service = FrequencyCapService()
    
    # Test valid evidence message
    ok, msg = service.evaluate_notification_eligibility(
        user_id="usr_101",
        product_id="style_3948102",
        message_text="3 buyers with your exact fit left reviews yesterday."
    )
    print(f"Test 1 (Valid): Eligible={ok}, Reason={msg}")

    # Test monetary violation message
    monetary_ok, monetary_msg = service.evaluate_notification_eligibility(
        user_id="usr_101",
        product_id="style_3948102",
        message_text="Price drop! Get 20% off on your wishlisted shirt."
    )
    print(f"Test 2 (Monetary Violation): Eligible={monetary_ok}, Reason={monetary_msg}")
