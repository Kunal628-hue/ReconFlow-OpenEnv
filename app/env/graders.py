from typing import List, Dict, Any, Tuple
from .models import Action, ActionType, InternalState

class ReconFlowGrader:
    def __init__(self, scenario: Dict[str, Any]):
        self.scenario = scenario

    def grade(self, state: InternalState) -> float:
        """
        Grades from 0.0 to 1.0.
        Dimensions:
        - Correct Decision (0.4)
        - Completeness of Analysis (0.3)
        - Safety (0.2)
        - Efficiency (0.1)
        """
        score = 0.0
        
        # Decision Correctness (0.4)
        if state.final_outcome == self.scenario["expected_resolution"]:
            score += 0.4
        
        # Completeness of Analysis (0.3)
        # Did the agent check the main documents before deciding?
        inspected = state.revealed_info
        if inspected["invoice"] and inspected["po"]:
            score += 0.1
        if inspected["goods_receipt"] or self.scenario.get("goods_receipt") is None:
            score += 0.1
        if inspected["vendor_profile"]:
            score += 0.1

        # Safety (0.2)
        # Avoid approving risky cases
        safety_bonus = 0.2
        if state.final_outcome == ActionType.APPROVE.value:
            if self.scenario.get("mismatches") or self.scenario.get("risks"):
              safety_bonus = 0.0 # Penalty for unsafe approval
            if "duplicate_invoice" in self.scenario.get("mismatches", []) and not state.is_duplicate_checked:
              safety_bonus = 0.0 # Penalty for not checking duplicates in risky scenario
        score += safety_bonus

        # Efficiency (0.1)
        # Reward finishing in few steps
        if state.elapsed_steps <= 10:
            score += 0.1
        elif state.elapsed_steps <= 15:
            score += 0.05

        final_score = min(max(round(score, 2), 0.0), 1.0)
        if final_score <= 0.0:
            return 0.01
        if final_score >= 1.0:
            return 0.99
        return final_score

    def explain_score(self, state: InternalState) -> Dict[str, Any]:
        return {
            "score": self.grade(state),
            "final_outcome": state.final_outcome,
            "expected_resolution": self.scenario["expected_resolution"],
            "steps": state.elapsed_steps,
            "inspected_info": state.revealed_info,
            "duplicate_checked": state.is_duplicate_checked
        }
