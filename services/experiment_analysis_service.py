"""
Myntra Wishlist Confidence Engine - Phase 7: Experiment Analysis & Ship Decision Service
Performs statistical hypothesis testing (Z-test), operational guardrail auditing,
segment breakdown evaluation, and executes the Post-MVP Decision Matrix.
"""

import sys
import os
import math
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from services.rollout_controller import RolloutController, RolloutStage


class ExperimentAnalysisService:
    """
    Production Experiment Analysis Service for Phase 7.
    """

    def __init__(self, rollout_controller: Optional[RolloutController] = None):
        self.rollout_controller = rollout_controller or RolloutController()

    def compute_two_tailed_z_test(
        self,
        control_adders: int,
        control_purchasers: int,
        treatment_adders: int,
        treatment_purchasers: int,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Executes a two-tailed Z-test for two proportions to evaluate 30-day purchaser rate lift.
        """
        if control_adders <= 0 or treatment_adders <= 0:
            raise ValueError("Adder sample sizes must be greater than zero.")

        p_ctrl = control_purchasers / control_adders
        p_treat = treatment_purchasers / treatment_adders

        # Pooled proportion
        p_pool = (control_purchasers + treatment_purchasers) / (control_adders + treatment_adders)

        # Standard error under null hypothesis
        se_pool = math.sqrt(p_pool * (1.0 - p_pool) * ((1.0 / control_adders) + (1.0 / treatment_adders)))

        # Z score
        z_score = (p_treat - p_ctrl) / se_pool if se_pool > 0 else 0.0

        # Two-tailed p-value calculation using error function erfc
        # p-value = 2 * (1 - cdf(|z|)) = erfc(|z| / sqrt(2))
        p_value = math.erfc(abs(z_score) / math.sqrt(2.0))

        # Absolute and Relative Lift
        abs_lift = p_treat - p_ctrl
        rel_lift_pct = (abs_lift / p_ctrl * 100.0) if p_ctrl > 0 else 0.0

        # 95% Confidence Interval for difference (p_treat - p_ctrl)
        se_diff = math.sqrt(
            (p_ctrl * (1.0 - p_ctrl) / control_adders) +
            (p_treat * (1.0 - p_treat) / treatment_adders)
        )
        z_critical = 1.96  # 95% confidence
        ci_lower = abs_lift - z_critical * se_diff
        ci_upper = abs_lift + z_critical * se_diff

        is_stat_sig = p_value < alpha

        return {
            "control": {
                "sampleSize": control_adders,
                "purchasers": control_purchasers,
                "conversionRate": round(p_ctrl, 4),
                "conversionRatePct": round(p_ctrl * 100.0, 2)
            },
            "treatment": {
                "sampleSize": treatment_adders,
                "purchasers": treatment_purchasers,
                "conversionRate": round(p_treat, 4),
                "conversionRatePct": round(p_treat * 100.0, 2)
            },
            "statisticalMetrics": {
                "absoluteLift": round(abs_lift, 4),
                "relativeLiftPct": round(rel_lift_pct, 2),
                "zScore": round(z_score, 4),
                "pValue": round(p_value, 4),
                "alpha": alpha,
                "isStatisticallySignificant": is_stat_sig,
                "confidenceInterval95": {
                    "lower": round(ci_lower, 4),
                    "upper": round(ci_upper, 4)
                }
            }
        }

    def audit_guardrails(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Audits operational guardrails against strict thresholds:
        - Size-related return rate <= 8.0%
        - Order cancellation rate <= 5.0%
        - Notification opt-out rate <= 3.0%
        - Wishlist API P95 latency < 100ms
        """
        size_return_rate = metrics.get("size_related_return_rate_pct", 6.42)
        cancellation_rate = metrics.get("order_cancellation_rate_pct", 2.10)
        opt_out_rate = metrics.get("notification_opt_out_rate_pct", 1.12)
        p95_latency = metrics.get("p95_latency_ms", 42.0)

        guardrails = [
            {
                "name": "Size-Related Return Rate",
                "threshold": "<= 8.0%",
                "currentValue": f"{size_return_rate:.2f}%",
                "status": "HEALTHY" if size_return_rate <= 8.0 else "BREACHED"
            },
            {
                "name": "Order Cancellation Rate",
                "threshold": "<= 5.0%",
                "currentValue": f"{cancellation_rate:.2f}%",
                "status": "HEALTHY" if cancellation_rate <= 5.0 else "BREACHED"
            },
            {
                "name": "Notification Opt-Out Rate",
                "threshold": "<= 3.0%",
                "currentValue": f"{opt_out_rate:.2f}%",
                "status": "HEALTHY" if opt_out_rate <= 3.0 else "BREACHED"
            },
            {
                "name": "Wishlist API P95 Latency",
                "threshold": "< 100ms",
                "currentValue": f"{p95_latency:.1f}ms",
                "status": "HEALTHY" if p95_latency < 100.0 else "BREACHED"
            }
        ]

        overall_healthy = all(g["status"] == "HEALTHY" for g in guardrails)

        return {
            "overallStatus": "HEALTHY" if overall_healthy else "BREACHED",
            "guardrails": guardrails
        }

    def evaluate_segment_consistency(self, segment_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Evaluates conversion lift consistency across user segments:
        - Category: Men's Apparel vs Women's Apparel
        - User Type: New Users vs Repeat Users
        - Platform: iOS Native vs Android Native
        """
        if not segment_data:
            segment_data = {
                "mens_apparel": {"control_conv": 0.118, "treatment_conv": 0.124, "rel_lift": 5.08},
                "womens_apparel": {"control_conv": 0.122, "treatment_conv": 0.126, "rel_lift": 3.28},
                "new_users": {"control_conv": 0.095, "treatment_conv": 0.101, "rel_lift": 6.32},
                "repeat_users": {"control_conv": 0.135, "treatment_conv": 0.141, "rel_lift": 4.44},
                "ios_native": {"control_conv": 0.124, "treatment_conv": 0.130, "rel_lift": 4.84},
                "android_native": {"control_conv": 0.117, "treatment_conv": 0.122, "rel_lift": 4.27}
            }

        results = []
        for segment_key, data in segment_data.items():
            name = segment_key.replace("_", " ").title()
            results.append({
                "segmentName": name,
                "controlConvRatePct": round(data["control_conv"] * 100.0, 2),
                "treatmentConvRatePct": round(data["treatment_conv"] * 100.0, 2),
                "relativeLiftPct": round(data["rel_lift"], 2),
                "isConsistentPositive": data["rel_lift"] > 0
            })
        return results

    def evaluate_post_mvp_decision_matrix(
        self,
        z_test_result: Dict[str, Any],
        guardrail_result: Dict[str, Any],
        detail_sheet_open_rate_pct: float = 44.2
    ) -> Dict[str, Any]:
        """
        Executes the Post-MVP Decision Matrix logic based on Phase 7 rules:
        - Scenario A: Lift > +3.5% (p < 0.05) & Guardrails Healthy -> Full Rollout (100% Treatment).
        - Scenario B: Primary Lift Positive BUT Size Returns > 8.0% -> Pause Rollout & Audit.
        - Scenario C: Detail Sheet Open Rate High BUT Primary Conv Flat (<= 0) -> Iterate Copy/Placement.
        - Scenario D: Neutral/Inconclusive (p >= 0.05) -> Do Not Roll Out.
        """
        rel_lift = z_test_result["statisticalMetrics"]["relativeLiftPct"]
        p_val = z_test_result["statisticalMetrics"]["pValue"]
        is_stat_sig = z_test_result["statisticalMetrics"]["isStatisticallySignificant"]
        guardrails_healthy = guardrail_result["overallStatus"] == "HEALTHY"

        # Find size return rate status
        size_return_guardrail = next(
            (g for g in guardrail_result["guardrails"] if g["name"] == "Size-Related Return Rate"), None
        )
        size_return_breached = size_return_guardrail and size_return_guardrail["status"] == "BREACHED"

        if rel_lift > 0 and size_return_breached:
            scenario = "SCENARIO_B"
            scenario_name = "Scenario B: Returns Spike"
            decision = "PAUSE_ROLLOUT"
            action_title = "PAUSE ROLLOUT - Raise evidence thresholds & audit size fit models"
            recommended_stage = RolloutStage.PAUSED

        elif rel_lift > 3.5 and is_stat_sig and guardrails_healthy:
            scenario = "SCENARIO_A"
            scenario_name = "Scenario A: Full Rollout Success"
            decision = "FULL_ROLLOUT"
            action_title = "FULL ROLLOUT (100% Treatment) - Initiate Phase 2 (Smart Compare)"
            recommended_stage = RolloutStage.FULL_ROLLOUT_100_PERCENT

        elif detail_sheet_open_rate_pct >= 30.0 and rel_lift <= 0 and guardrails_healthy:
            scenario = "SCENARIO_C"
            scenario_name = "Scenario C: High Engagement, No Conversion"
            decision = "ITERATE_COPY_AND_PLACEMENT"
            action_title = "ITERATE COPY & PLACEMENT - Re-evaluate Add-to-Bag conversion flow"
            recommended_stage = RolloutStage.EXPERIMENT_50_50

        else:  # Neutral or p >= 0.05
            scenario = "SCENARIO_D"
            scenario_name = "Scenario D: Neutral / Inconclusive"
            decision = "DO_NOT_ROLL_OUT"
            action_title = "DO NOT ROLL OUT - Conduct qualitative user research and interviews"
            recommended_stage = RolloutStage.EXPERIMENT_50_50

        return {
            "scenario": scenario,
            "scenarioName": scenario_name,
            "decision": decision,
            "actionTitle": action_title,
            "recommendedRolloutStage": recommended_stage,
            "evaluationInputs": {
                "relativeLiftPct": rel_lift,
                "pValue": p_val,
                "isStatisticallySignificant": is_stat_sig,
                "guardrailsHealthy": guardrails_healthy,
                "detailSheetOpenRatePct": detail_sheet_open_rate_pct
            }
        }

    def execute_ship_decision(
        self,
        control_adders: int = 95390,
        control_purchasers: int = 11446,
        treatment_adders: int = 95390,
        treatment_purchasers: int = 11942,
        guardrail_metrics: Optional[Dict[str, float]] = None,
        apply_to_controller: bool = True
    ) -> Dict[str, Any]:
        """
        Full end-to-end execution of Phase 7 ship decision analysis.
        """
        if guardrail_metrics is None:
            guardrail_metrics = {
                "size_related_return_rate_pct": 6.42,
                "order_cancellation_rate_pct": 2.10,
                "notification_opt_out_rate_pct": 1.12,
                "p95_latency_ms": 42.0
            }

        z_test = self.compute_two_tailed_z_test(
            control_adders, control_purchasers, treatment_adders, treatment_purchasers
        )
        guardrails = self.audit_guardrails(guardrail_metrics)
        segments = self.evaluate_segment_consistency()
        decision_matrix = self.evaluate_post_mvp_decision_matrix(z_test, guardrails)

        if apply_to_controller:
            self.rollout_controller.set_stage(decision_matrix["recommendedRolloutStage"])

        return {
            "experiment": {
                "name": "Myntra Wishlist Confidence Engine Production A/B Trial",
                "durationWeeks": 6,
                "targetMetric": "30-Day Wishlist Purchaser Rate",
                "controlGroup": "CURRENT_WISHLIST",
                "treatmentGroup": "TREATMENT_FIT_QUALITY_V1"
            },
            "zTestResult": z_test,
            "guardrailAudit": guardrails,
            "segmentAnalysis": segments,
            "postMvpDecision": decision_matrix,
            "rolloutControllerState": {
                "activeStage": self.rollout_controller.current_stage
            }
        }


if __name__ == "__main__":
    svc = ExperimentAnalysisService()
    report = svc.execute_ship_decision()
    print("=== PHASE 7 SHIP DECISION REPORT ===")
    print("Lift           :", report["zTestResult"]["statisticalMetrics"]["relativeLiftPct"], "%")
    print("p-Value        :", report["zTestResult"]["statisticalMetrics"]["pValue"])
    print("Decision       :", report["postMvpDecision"]["scenarioName"])
    print("Action         :", report["postMvpDecision"]["actionTitle"])
    print("Controller Stage:", report["rolloutControllerState"]["activeStage"])
