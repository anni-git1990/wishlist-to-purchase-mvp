"""
Myntra Wishlist Confidence Engine - Kafka Event Taxonomy Validator
Validates incoming analytics payloads against the 15 required event JSON Schemas.
Includes a fallback validator if external `jsonschema` package is missing.
"""

import json
import os
from typing import Dict, Any, Tuple

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMAS_DIR = os.path.dirname(os.path.abspath(__file__))

EVENT_CATALOG = [
    "wishlist_item_added",
    "wishlist_viewed",
    "wishlist_item_revisited",
    "fit_confidence_impression",
    "fit_confidence_opened",
    "size_recommendation_selected",
    "quality_digest_impression",
    "quality_digest_opened",
    "customer_evidence_opened",
    "confidence_feedback_submitted",
    "wishlist_trigger_sent",
    "wishlist_trigger_opened",
    "wishlist_item_added_to_bag",
    "wishlisted_item_purchased",
    "wishlisted_item_returned"
]

class EventValidator:
    def __init__(self, schemas_dir: str = SCHEMAS_DIR):
        self.schemas_dir = schemas_dir
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self._load_schemas()

    def _load_schemas(self):
        for event_name in EVENT_CATALOG:
            schema_file = os.path.join(self.schemas_dir, f"{event_name}.json")
            if os.path.exists(schema_file):
                with open(schema_file, 'r', encoding='utf-8') as f:
                    self.schemas[event_name] = json.load(f)

    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, str]:
        event_name = payload.get("eventName")
        if not event_name:
            return False, "Missing 'eventName' in event payload"

        if event_name not in self.schemas:
            return False, f"Unknown eventName '{event_name}'. Allowed: {EVENT_CATALOG}"

        schema = self.schemas[event_name]
        
        if HAS_JSONSCHEMA:
            try:
                jsonschema.validate(instance=payload, schema=schema)
                return True, "Valid"
            except jsonschema.ValidationError as err:
                return False, f"Schema validation error for '{event_name}': {err.message}"
            except jsonschema.SchemaError as err:
                return False, f"Schema error for '{event_name}': {err.message}"
        else:
            # Fallback lightweight validator
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in payload:
                    return False, f"Missing required property '{field}' for event '{event_name}'"
            return True, "Valid (Lightweight Fallback)"


if __name__ == "__main__":
    validator = EventValidator()
    print(f"Loaded {len(validator.schemas)} event schemas successfully. HAS_JSONSCHEMA={HAS_JSONSCHEMA}")
