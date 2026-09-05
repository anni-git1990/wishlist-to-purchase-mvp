"""
Myntra Wishlist Confidence Engine - Kafka Event Ingestion & Flink Stream Processor
Ingests client events, validates JSON schema, and processes real-time 30-day conversion attribution.
"""

from typing import Dict, Any, List, Tuple
from schemas.events.validator import EventValidator
from services.ab_assignment_service import ABAssignmentService, CONTROL_GROUP, TREATMENT_GROUP


class EventIngestionService:
    def __init__(self):
        self.validator = EventValidator()
        self.ab_service = ABAssignmentService()
        self.ingested_events: List[Dict[str, Any]] = []
        
        # Real-Time Flink Attribution Aggregates
        self.attribution_store: Dict[str, Dict[str, Any]] = {
            CONTROL_GROUP: {
                "wishlistAdders": 0,
                "wishlistPurchasers30d": 0,
                "totalPurchases": 0,
                "totalReturns": 0,
                "fitReturns": 0
            },
            TREATMENT_GROUP: {
                "wishlistAdders": 0,
                "wishlistPurchasers30d": 0,
                "totalPurchases": 0,
                "totalReturns": 0,
                "fitReturns": 0
            }
        }

    def ingest_event(self, event_payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates and ingests analytics tracking event into Kafka stream pipeline.
        """
        is_valid, msg = self.validator.validate(event_payload)
        if not is_valid:
            return False, f"Ingestion Rejected: {msg}"

        # Assign experiment group if missing
        user_id = event_payload.get("userId")
        exp_group = event_payload.get("experimentGroup")
        if not exp_group and user_id:
            exp_group = self.ab_service.get_assignment(user_id)["experimentGroup"]
            event_payload["experimentGroup"] = exp_group

        self.ingested_events.append(event_payload)
        
        # Process Flink Stream Attribution
        self._process_stream_attribution(event_payload)
        return True, "Event Ingested Successfully"

    def _process_stream_attribution(self, event: Dict[str, Any]):
        event_name = event.get("eventName")
        exp_group = event.get("experimentGroup", CONTROL_GROUP)
        
        if exp_group not in self.attribution_store:
            exp_group = CONTROL_GROUP

        group_stats = self.attribution_store[exp_group]

        if event_name == "wishlist_item_added":
            group_stats["wishlistAdders"] += 1

        elif event_name == "wishlisted_item_purchased":
            group_stats["totalPurchases"] += 1
            if event.get("wasPurchasedWithin30Days", False):
                group_stats["wishlistPurchasers30d"] += 1

        elif event_name == "wishlisted_item_returned":
            group_stats["totalReturns"] += 1
            reason = event.get("returnReason", "")
            if "FIT" in reason or "SIZE" in reason:
                group_stats["fitReturns"] += 1

    def get_attribution_summary(self) -> Dict[str, Any]:
        """
        Computes 30-day Wishlist Purchaser Rate and Lift metrics for Control vs Treatment.
        """
        ctrl = self.attribution_store[CONTROL_GROUP]
        treat = self.attribution_store[TREATMENT_GROUP]

        ctrl_rate = (ctrl["wishlistPurchasers30d"] / ctrl["wishlistAdders"]) if ctrl["wishlistAdders"] > 0 else 0.0
        treat_rate = (treat["wishlistPurchasers30d"] / treat["wishlistAdders"]) if treat["wishlistAdders"] > 0 else 0.0

        abs_lift = treat_rate - ctrl_rate
        rel_lift = (abs_lift / ctrl_rate * 100) if ctrl_rate > 0 else 0.0

        ctrl_return_rate = (ctrl["fitReturns"] / ctrl["totalPurchases"]) if ctrl["totalPurchases"] > 0 else 0.0
        treat_return_rate = (treat["fitReturns"] / treat["totalPurchases"]) if treat["totalPurchases"] > 0 else 0.0

        return {
            "control": {
                "groupName": CONTROL_GROUP,
                "wishlistAdders": ctrl["wishlistAdders"],
                "purchasers30d": ctrl["wishlistPurchasers30d"],
                "conversionRate": round(ctrl_rate, 4),
                "fitReturnRate": round(ctrl_return_rate, 4)
            },
            "treatment": {
                "groupName": TREATMENT_GROUP,
                "wishlistAdders": treat["wishlistAdders"],
                "purchasers30d": treat["wishlistPurchasers30d"],
                "conversionRate": round(treat_rate, 4),
                "fitReturnRate": round(treat_return_rate, 4)
            },
            "metrics": {
                "absoluteLift": round(abs_lift, 4),
                "relativeLiftPercentage": round(rel_lift, 2),
                "guardrailReturnSpike": treat_return_rate > (ctrl_return_rate + 0.08)
            }
        }


if __name__ == "__main__":
    service = EventIngestionService()
    
    # Ingest sample event
    sample_event = {
        "eventId": "evt_001",
        "eventName": "wishlist_item_added",
        "timestamp": "2026-09-04T16:00:00Z",
        "userId": "usr_98745210",
        "productId": "style_3948102",
        "variantId": "sku_991823",
        "sourceSurface": "PDP"
    }
    success, msg = service.ingest_event(sample_event)
    print(f"Ingest Result: {success}, Msg: {msg}")
    print(f"Attribution Summary: {service.get_attribution_summary()}")
