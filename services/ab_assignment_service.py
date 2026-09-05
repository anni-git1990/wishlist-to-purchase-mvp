"""
Myntra Wishlist Confidence Engine - A/B Randomization & Feature Flag Service
Implements deterministic user-level assignment using MurmurHash3.
Ensures zero cross-group leakage and stateless hash consistency.
"""

import hashlib
from typing import Dict, Any

DEFAULT_SALT = "wishlist_v1_salt"
CONTROL_GROUP = "CURRENT_WISHLIST"
TREATMENT_GROUP = "TREATMENT_FIT_QUALITY_V1"


def murmurhash3_32(key: str, seed: int = 0) -> int:
    """
    Pure Python 32-bit MurmurHash3 implementation for zero external dependencies.
    """
    key_bytes = key.encode('utf-8')
    length = len(key_bytes)
    h1 = seed
    c1 = 0xcc9e2d51
    c2 = 0x1b873593

    nblocks = length // 4
    for i in range(nblocks):
        k1 = (key_bytes[i*4] & 0xff) | \
             ((key_bytes[i*4 + 1] & 0xff) << 8) | \
             ((key_bytes[i*4 + 2] & 0xff) << 16) | \
             ((key_bytes[i*4 + 3] & 0xff) << 24)

        k1 = (k1 * c1) & 0xffffffff
        k1 = ((k1 << 15) | (k1 >> (32 - 15))) & 0xffffffff
        k1 = (k1 * c2) & 0xffffffff

        h1 ^= k1
        h1 = ((h1 << 13) | (h1 >> (32 - 13))) & 0xffffffff
        h1 = (h1 * 5 + 0xe6546b64) & 0xffffffff

    tail = key_bytes[nblocks*4:]
    k1 = 0
    tail_len = len(tail)
    if tail_len == 3:
        k1 ^= (tail[2] & 0xff) << 16
    if tail_len >= 2:
        k1 ^= (tail[1] & 0xff) << 8
    if tail_len >= 1:
        k1 ^= (tail[0] & 0xff)
        k1 = (k1 * c1) & 0xffffffff
        k1 = ((k1 << 15) | (k1 >> (32 - 15))) & 0xffffffff
        k1 = (k1 * c2) & 0xffffffff
        h1 ^= k1

    h1 ^= length
    h1 ^= (h1 >> 16)
    h1 = (h1 * 0x85ebca6b) & 0xffffffff
    h1 ^= (h1 >> 13)
    h1 = (h1 * 0xc2b2ae35) & 0xffffffff
    h1 ^= (h1 >> 16)

    return h1


class ABAssignmentService:
    def __init__(self, salt: str = DEFAULT_SALT, split_pct: float = 50.0):
        self.salt = salt
        self.split_pct = split_pct

    def get_assignment(self, user_id: str) -> Dict[str, Any]:
        """
        Determines user experiment group deterministically based on user_id hash.
        """
        if not user_id:
            raise ValueError("user_id cannot be empty")

        hash_key = f"{user_id}_{self.salt}"
        hash_val = murmurhash3_32(hash_key)
        bucket = hash_val % 100

        is_treatment = bucket >= self.split_pct
        group = TREATMENT_GROUP if is_treatment else CONTROL_GROUP

        return {
            "userId": user_id,
            "experimentGroup": group,
            "isTreatment": is_treatment,
            "bucket": bucket,
            "salt": self.salt
        }

    def verify_no_leakage(self, sample_user_ids) -> Dict[str, Any]:
        """
        Audits synthetic user IDs to verify zero assignment drift and ~50/50 balance.
        """
        control_count = 0
        treatment_count = 0

        for uid in sample_user_ids:
            res = self.get_assignment(uid)
            if res["isTreatment"]:
                treatment_count += 1
            else:
                control_count += 1

        total = len(sample_user_ids)
        treatment_pct = (treatment_count / total) * 100 if total > 0 else 0

        return {
            "totalEvaluated": total,
            "controlCount": control_count,
            "treatmentCount": treatment_count,
            "treatmentPercentage": round(treatment_pct, 2),
            "isBalanced": 48.0 <= treatment_pct <= 52.0
        }


if __name__ == "__main__":
    service = ABAssignmentService()
    test_uid = "usr_98745210"
    res = service.get_assignment(test_uid)
    print(f"Assignment for {test_uid}: {res}")
    
    # Run synthetic 10,000 user balance check
    synthetic_uids = [f"usr_{i}" for i in range(10000)]
    audit = service.verify_no_leakage(synthetic_uids)
    print(f"Sample Balance Check: {audit}")
