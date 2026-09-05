"""
Unit and Integration Test Suite for Phase 7 Deliverables (Production A/B Experiment & Ship Decision)
Tests:
1. Two-tailed Z-test statistical hypothesis evaluation (Z-score, p-value, 95% CI, relative lift).
2. Operational guardrails health auditing (healthy thresholds vs breached thresholds).
3. Segment breakdown consistency evaluation (Men's/Women's, New/Repeat, iOS/Android).
4. Post-MVP Decision Matrix evaluation across all 4 scenarios (A, B, C, D).
5. Dynamic rollout stage execution on RolloutController.
"""

import sys
import os
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.experiment_analysis_service import ExperimentAnalysisService
from services.rollout_controller import RolloutController, RolloutStage


class TestPhase7Deliverables(unittest.TestCase):

    def setUp(self):
        self.rollout_ctrl = RolloutController()
        self.analysis_svc = ExperimentAnalysisService(rollout_controller=self.rollout_ctrl)

    def test_two_tailed_z_test_calculation(self):
        # Control: 95,390 adders, 11,446 purchasers (12.00%)
        # Treatment: 95,390 adders, 11,942 purchasers (12.52%)
        res = self.analysis_svc.compute_two_tailed_z_test(
            control_adders=95390,
            control_purchasers=11446,
            treatment_adders=95390,
            treatment_purchasers=11942
        )

        self.assertEqual(res["control"]["conversionRatePct"], 12.00)
        self.assertEqual(res["treatment"]["conversionRatePct"], 12.52)
        self.assertAlmostEqual(res["statisticalMetrics"]["relativeLiftPct"], 4.33, delta=0.1)
        self.assertTrue(res["statisticalMetrics"]["isStatisticallySignificant"])
        self.assertLess(res["statisticalMetrics"]["pValue"], 0.05)
        self.assertIn("lower", res["statisticalMetrics"]["confidenceInterval95"])
        self.assertIn("upper", res["statisticalMetrics"]["confidenceInterval95"])

    def test_guardrail_auditor_healthy_and_breached(self):
        healthy_metrics = {
            "size_related_return_rate_pct": 6.42,
            "order_cancellation_rate_pct": 2.10,
            "notification_opt_out_rate_pct": 1.12,
            "p95_latency_ms": 42.0
        }
        res_healthy = self.analysis_svc.audit_guardrails(healthy_metrics)
        self.assertEqual(res_healthy["overallStatus"], "HEALTHY")

        breached_metrics = {
            "size_related_return_rate_pct": 9.20,  # > 8.0%
            "order_cancellation_rate_pct": 2.10,
            "notification_opt_out_rate_pct": 1.12,
            "p95_latency_ms": 42.0
        }
        res_breached = self.analysis_svc.audit_guardrails(breached_metrics)
        self.assertEqual(res_breached["overallStatus"], "BREACHED")

    def test_segment_consistency_evaluation(self):
        segments = self.analysis_svc.evaluate_segment_consistency()
        self.assertGreaterEqual(len(segments), 4)
        segment_names = [s["segmentName"] for s in segments]
        self.assertIn("Mens Apparel", segment_names)
        self.assertIn("Ios Native", segment_names)
        for s in segments:
            self.assertTrue(s["isConsistentPositive"])

    def test_post_mvp_decision_matrix_scenario_a_success(self):
        z_test = self.analysis_svc.compute_two_tailed_z_test(95390, 11446, 95390, 11942)
        guardrails = self.analysis_svc.audit_guardrails({"size_related_return_rate_pct": 6.42})

        decision = self.analysis_svc.evaluate_post_mvp_decision_matrix(z_test, guardrails)
        self.assertEqual(decision["scenario"], "SCENARIO_A")
        self.assertEqual(decision["decision"], "FULL_ROLLOUT")
        self.assertEqual(decision["recommendedRolloutStage"], RolloutStage.FULL_ROLLOUT_100_PERCENT)

    def test_post_mvp_decision_matrix_scenario_b_returns_spike(self):
        z_test = self.analysis_svc.compute_two_tailed_z_test(95390, 11446, 95390, 11942)
        # Breached return rate > 8.0%
        guardrails = self.analysis_svc.audit_guardrails({"size_related_return_rate_pct": 9.50})

        decision = self.analysis_svc.evaluate_post_mvp_decision_matrix(z_test, guardrails)
        self.assertEqual(decision["scenario"], "SCENARIO_B")
        self.assertEqual(decision["decision"], "PAUSE_ROLLOUT")
        self.assertEqual(decision["recommendedRolloutStage"], RolloutStage.PAUSED)

    def test_post_mvp_decision_matrix_scenario_c_high_engagement_low_conversion(self):
        # Flat conversion (control == treatment)
        z_test = self.analysis_svc.compute_two_tailed_z_test(95390, 11446, 95390, 11446)
        guardrails = self.analysis_svc.audit_guardrails({"size_related_return_rate_pct": 6.42})

        decision = self.analysis_svc.evaluate_post_mvp_decision_matrix(
            z_test, guardrails, detail_sheet_open_rate_pct=42.0
        )
        self.assertEqual(decision["scenario"], "SCENARIO_C")
        self.assertEqual(decision["decision"], "ITERATE_COPY_AND_PLACEMENT")

    def test_post_mvp_decision_matrix_scenario_d_neutral(self):
        # Small non-statistically significant sample size or tiny lift
        z_test = self.analysis_svc.compute_two_tailed_z_test(100, 12, 100, 12)
        guardrails = self.analysis_svc.audit_guardrails({"size_related_return_rate_pct": 6.42})

        decision = self.analysis_svc.evaluate_post_mvp_decision_matrix(
            z_test, guardrails, detail_sheet_open_rate_pct=10.0
        )
        self.assertEqual(decision["scenario"], "SCENARIO_D")
        self.assertEqual(decision["decision"], "DO_NOT_ROLL_OUT")

    def test_full_ship_decision_execution_and_rollout_stage_toggling(self):
        report = self.analysis_svc.execute_ship_decision()
        self.assertEqual(report["postMvpDecision"]["scenario"], "SCENARIO_A")
        # Verify controller stage was updated to FULL_ROLLOUT_100_PERCENT
        self.assertEqual(self.rollout_ctrl.current_stage, RolloutStage.FULL_ROLLOUT_100_PERCENT)

        # Check exposure evaluation under full rollout stage
        eval_res = self.rollout_ctrl.evaluate_user_exposure("usr_any_user")
        self.assertTrue(eval_res["receiveTreatment"])
        self.assertEqual(eval_res["experimentGroup"], "TREATMENT_FIT_QUALITY_V1")


if __name__ == "__main__":
    unittest.main()
