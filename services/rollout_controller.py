"""
Myntra Wishlist Confidence Engine - Staged Rollout Exposure Controller
Manages progressive traffic exposure phases (Dogfooding -> 1% -> 5% -> 50/50 Experiment).
"""

from typing import Dict, Any
from services.ab_assignment_service import ABAssignmentService


class RolloutStage:
    DOGFOODING = "DOGFOODING"              # Internal staff only
    ROLLOUT_1_PCT = "ROLLOUT_1_PCT"        # 1% production traffic
    ROLLOUT_5_PCT = "ROLLOUT_5_PCT"        # 5% production traffic
    EXPERIMENT_50_50 = "EXPERIMENT_50_50"  # Full 50/50 A/B experiment
    FULL_ROLLOUT_100_PERCENT = "FULL_ROLLOUT_100_PERCENT"  # 100% treatment rollout
    PAUSED = "PAUSED"                      # Rollout paused / suppressed


class RolloutController:
    def __init__(self, stage: str = RolloutStage.EXPERIMENT_50_50):
        self.current_stage = stage
        self.ab_service = ABAssignmentService()

    def set_stage(self, stage: str):
        self.current_stage = stage

    def evaluate_user_exposure(self, user_id: str, is_internal_staff: bool = False) -> Dict[str, Any]:
        """
        Evaluates whether a user receives Treatment feature experience under current rollout stage.
        """
        assignment = self.ab_service.get_assignment(user_id)
        bucket = assignment["bucket"]
        is_ab_treatment = assignment["isTreatment"]

        if self.current_stage == RolloutStage.DOGFOODING:
            # Only internal staff receive treatment
            receive_treatment = is_internal_staff
            reason = "Internal Staff Dogfooding" if is_internal_staff else "Non-staff suppressed during dogfooding"

        elif self.current_stage == RolloutStage.ROLLOUT_1_PCT:
            receive_treatment = is_internal_staff or (bucket < 1)
            reason = "1% Staged Exposure" if receive_treatment else "Outside 1% bucket"

        elif self.current_stage == RolloutStage.ROLLOUT_5_PCT:
            receive_treatment = is_internal_staff or (bucket < 5)
            reason = "5% Staged Exposure" if receive_treatment else "Outside 5% bucket"

        elif self.current_stage == RolloutStage.FULL_ROLLOUT_100_PERCENT:
            receive_treatment = True
            reason = "100% Full Production Rollout"

        elif self.current_stage == RolloutStage.PAUSED:
            receive_treatment = False
            reason = "Rollout Paused (Suppressed)"

        else:  # RolloutStage.EXPERIMENT_50_50
            receive_treatment = is_ab_treatment
            reason = "50/50 A/B Experiment Treatment" if is_ab_treatment else "50/50 Control Group"

        return {
            "userId": user_id,
            "stage": self.current_stage,
            "receiveTreatment": receive_treatment,
            "experimentGroup": "TREATMENT_FIT_QUALITY_V1" if receive_treatment else "CURRENT_WISHLIST",
            "bucket": bucket,
            "reason": reason
        }


if __name__ == "__main__":
    controller = RolloutController(RolloutStage.DOGFOODING)
    print("Dogfooding (Staff):", controller.evaluate_user_exposure("usr_101", is_internal_staff=True)["receiveTreatment"])
    print("Dogfooding (External):", controller.evaluate_user_exposure("usr_101", is_internal_staff=False)["receiveTreatment"])

    controller.set_stage(RolloutStage.EXPERIMENT_50_50)
    print("50/50 Experiment:", controller.evaluate_user_exposure("usr_98745210")["experimentGroup"])
