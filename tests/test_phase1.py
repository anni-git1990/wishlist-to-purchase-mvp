"""
Unit and Integration Test Suite for Phase 1 Deliverables (Standard unittest)
Tests:
1. All 15 Event JSON Schemas via EventValidator.
2. PostgreSQL DDL SQL File Existence and Structure.
3. MongoDB JSON Schema Syntax.
4. OpenAPI Spec File Validity.
5. Statistical Sample Size & MDE Calculations.
"""

import sys
import os
import json
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from schemas.events.validator import EventValidator, EVENT_CATALOG
from scripts.data_audit_and_baseline import calculate_sample_size, run_data_audit


class TestPhase1Deliverables(unittest.TestCase):

    def test_event_schemas_exist_and_validate(self):
        validator = EventValidator()
        self.assertEqual(len(validator.schemas), 15, f"Expected 15 event schemas, found {len(validator.schemas)}")
        
        # Test valid payload for wishlist_item_added
        sample_payload = {
            "eventId": "evt_1001",
            "eventName": "wishlist_item_added",
            "timestamp": "2026-09-04T15:00:00Z",
            "userId": "usr_9988",
            "productId": "style_3948102",
            "variantId": "sku_991823",
            "sourceSurface": "PDP"
        }
        is_valid, msg = validator.validate(sample_payload)
        self.assertTrue(is_valid, f"Validation failed for wishlist_item_added: {msg}")

    def test_all_15_events_have_valid_schemas(self):
        validator = EventValidator()
        for event_name in EVENT_CATALOG:
            self.assertIn(event_name, validator.schemas, f"Missing schema for event '{event_name}'")
            schema = validator.schemas[event_name]
            self.assertTrue(schema.get("title"), f"Schema for {event_name} missing 'title'")
            self.assertIn("properties", schema, f"Schema for {event_name} missing 'properties'")

    def test_postgresql_ddl_file_exists_and_valid(self):
        ddl_path = os.path.join(BASE_DIR, "db", "migrations", "001_initial_schema.sql")
        self.assertTrue(os.path.exists(ddl_path), f"PostgreSQL DDL script not found at {ddl_path}")
        with open(ddl_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CREATE TABLE IF NOT EXISTS wishlist_items", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS user_fit_profiles", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS fit_recommendation_logs", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS notification_trigger_logs", content)

    def test_mongodb_json_schema_valid(self):
        mongo_schema_path = os.path.join(BASE_DIR, "db", "mongo", "product_quality_digests_schema.json")
        self.assertTrue(os.path.exists(mongo_schema_path))
        with open(mongo_schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        self.assertIn("$jsonSchema", schema)

    def test_openapi_spec_file_exists(self):
        openapi_path = os.path.join(BASE_DIR, "api", "openapi.yaml")
        self.assertTrue(os.path.exists(openapi_path))
        with open(openapi_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("openapi: 3.0.3", content)
        self.assertIn("/wishlist/{userId}/confidence", content)
        self.assertIn("/products/{productId}/fit-confidence", content)
        self.assertIn("/products/{productId}/quality-digest", content)

    def test_statistical_power_calculator(self):
        res = calculate_sample_size(p1=0.12, mde_relative=0.035, alpha=0.05, power=0.80)
        self.assertEqual(res["baseline_rate_p1"], 0.12)
        self.assertGreater(res["target_rate_p2"], 0.12)
        self.assertGreater(res["required_sample_size_per_group"], 90000)
        self.assertEqual(res["total_required_sample_size"], res["required_sample_size_per_group"] * 2)

    def test_run_data_audit_script(self):
        audit_data = run_data_audit()
        self.assertIn("catalog_audit", audit_data)
        self.assertIn("historical_baseline", audit_data)
        self.assertIn("experiment_power_analysis", audit_data)

if __name__ == "__main__":
    unittest.main()
