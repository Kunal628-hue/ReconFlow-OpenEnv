from typing import List, Dict, Any, Tuple
from .models import Action, ActionType, InternalState
from .scoring_utils import sanitize_score

class RewardCalculator:
    def __init__(self, scenario: Dict[str, Any]):
        self.scenario = scenario

    def calculate_final_reward(self, state: InternalState) -> float:
        """
        Final reward based on decision correctness.
        """
        outcome = state.final_outcome
        expected = self.scenario.get("expected_resolution")
        
        if outcome == expected:
            return sanitize_score(0.5)  # Success reward
        
        # Severe penalties for risky mis-approvals
        if outcome == ActionType.APPROVE.value:
            if self.scenario.get("mismatches") or self.scenario.get("risks"):
                return sanitize_score(-1.0)
        
        # Penalize unnecessary escalations
        if outcome == ActionType.ESCALATE_MANAGER.value and expected == ActionType.APPROVE.value:
            return sanitize_score(-0.2)
        
        return sanitize_score(-0.5)

    def calculate_step_reward(self, state: InternalState, action: Action) -> float:
        """
        Partial rewards for correct actions.
        """
        # Deduplicate actions
        if state.actions_taken.count(action) > 1:
            return sanitize_score(-0.1)  # Redundant action penalty
        
        # Check relevant document reward
        at = action.action_type
        if at == ActionType.INSPECT_INVOICE:
            return sanitize_score(0.1)
        if at == ActionType.INSPECT_PO:
            return sanitize_score(0.1)
        if at == ActionType.INSPECT_GOODS_RECEIPT:
            return sanitize_score(0.1)
        if at == ActionType.CHECK_DUPLICATE_INVOICE and self.scenario.get("task_id") in ["medium", "hard"]:
            return sanitize_score(0.1)
        if at == ActionType.FLAG_MISMATCH and self.scenario.get("mismatches"):
            return sanitize_score(0.2)
        if at == ActionType.FLAG_FRAUD_RISK and self.scenario.get("risks"):
            return sanitize_score(0.2)
        
        return sanitize_score(0.0)
