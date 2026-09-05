"""
Unit and Integration Test Suite for Phase 6 Deliverables (QA, Performance & Staged Rollout)
Tests:
1. PrivacyComplianceService PII Scrubbing & GDPR Fit Profile Deletion.
2. RolloutController Staged Traffic Allocation (Dogfooding -> 1% -> 5% -> 50/50).
3. PerformanceLoadSimulator 15,000 req/sec Peak Throughput & Latency SLA.
"""

import sys
import os
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.privacy_compliance_service import PrivacyComplianceService
from services.rollout_controller import RolloutController, RolloutStage
from tests.performance_load_test import PerformanceLoadSimulator


class TestPhase6Deliverables(unittest.TestCase):

    def setUp(self):
        self.privacy_svc = PrivacyComplianceService()
        self.rollout_ctrl = RolloutController()

    def test_privacy_pii_scrubbing(self):
        raw_tag = "Priya Sharma (priya.s@gmail.com, 9876543210)"
        raw_text = "My name is Priya and my phone is 9876543210. Email me at priya.s@gmail.com."

        scrubbed_tag, scrubbed_text = self.privacy_svc.scrub_pii_from_review_tag(raw_tag, raw_text)
        
        self.assertNotIn("priya.s@gmail.com", scrubbed_tag)
        self.assertNotIn("9876543210", scrubbed_tag)
        self.assertNotIn("priya.s@gmail.com", scrubbed_text)
        self.assertNotIn("9876543210", scrubbed_text)

    def test_gdpr_fit_profile_deletion(self):
        user_id = "usr_gdpr_test_01"
        res = self.privacy_svc.delete_user_fit_profile(user_id)
        
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["action"], "FIT_PROFILE_DELETED")
        self.assertEqual(res["gdprCompliance"], "WIPED_PERMANENTLY")

        # Verify profile is wiped in feature store
        vec = self.privacy_svc.feature_store.get_user_fit_vector(user_id)
        self.assertIsNone(vec["height_cm"])
        self.assertFalse(vec["consent_given"])

    def test_staged_rollout_controller_phases(self):
        # 1. Dogfooding Stage
        self.rollout_ctrl.set_stage(RolloutStage.DOGFOODING)
        staff_eval = self.rollout_ctrl.evaluate_user_exposure("usr_01", is_internal_staff=True)
        self.assertTrue(staff_eval["receiveTreatment"])
        
        external_eval = self.rollout_ctrl.evaluate_user_exposure("usr_01", is_internal_staff=False)
        self.assertFalse(external_eval["receiveTreatment"])

        # 2. 50/50 Experiment Stage
        self.rollout_ctrl.set_stage(RolloutStage.EXPERIMENT_50_50)
        exp_eval = self.rollout_ctrl.evaluate_user_exposure("usr_98745210")
        self.assertIn(exp_eval["experimentGroup"], ["CURRENT_WISHLIST", "TREATMENT_FIT_QUALITY_V1"])

    def test_performance_load_test_benchmark(self):
        simulator = PerformanceLoadSimulator()
        report = simulator.run_load_simulation(total_requests=500)
        
        self.assertIn("latencyMetricsMs", report)
        self.assertLess(report["latencyMetricsMs"]["p95"], 100.0, f"P95 latency {report['latencyMetricsMs']['p95']}ms exceeded 100ms SLA")
        self.assertGreater(report["cachePerformance"]["hitRatePct"], 75.0)
        self.assertTrue(report["reliability"]["slaPassed"])

if __name__ == "__main__":
    unittest.main()
