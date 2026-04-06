from typing import Tuple, Dict, Any, List, Optional
from .models import (
    Action, ActionType, Observation, StepResult, InternalState, 
    CaseStage, MismatchFlag, RiskFlag
)
import datetime

class ReconFlowStateMachine:
    def __init__(self, scenario: Dict[str, Any], max_steps: int = 15):
        self.scenario = scenario
        self.max_steps = max_steps
        self.state = InternalState(case_data=scenario)
        self._initial_notes = f"Case {scenario['id']} assigned. Please review for payment approval."

    def reset(self) -> Observation:
        self.state = InternalState(case_data=self.scenario)
        return self._get_observation()

    def _get_observation(self) -> Observation:
        revealed = self.state.revealed_info
        case = self.state.case_data
        
        # Partially mask data based on what's revealed
        invoice_summary = {
            "invoice_number": case["invoice"]["invoice_number"],
            "vendor_id": case["invoice"]["vendor_id"],
            "total_amount": case["invoice"]["total_amount"]
        } if revealed["invoice"] else None
        
        po_summary = {
            "po_number": case["po"].get("po_number", "PO_UNKNOWN"),
            "total_amount": case["po"].get("total_amount", 0.0)
        } if revealed["po"] and case["po"] else ({"po_number": "NOT_FOUND"} if revealed["po"] else None)

        gr_summary = {
            "gr_number": case["goods_receipt"].get("gr_number", "SERVICE_CONF"),
            "received_status": "Confirmed"
        } if revealed["goods_receipt"] and case["goods_receipt"] else ({"received_status": "PENDING"} if revealed["goods_receipt"] else None)

        vendor_profile = {
            "name": case["vendor_profile"].get("name"),
            "risk_rating": case["vendor_profile"].get("risk_rating", "Unknown")
        } if revealed["vendor_profile"] else None

        # Logic for flags - only show flags if relevant check was performed
        mismatch_flags = []
        if self.state.is_duplicate_checked and "duplicate_invoice" in case.get("mismatches", []):
          mismatch_flags.append(MismatchFlag.DUPLICATE_INVOICE)

        # Notes/Status
        status = "Reviewing"
        if self.state.final_outcome:
            status = f"Finished - {self.state.final_outcome}"
        elif self.state.elapsed_steps == 0:
            status = "Initial"

        return Observation(
            case_id=case["id"],
            task_id=case["task_id"],
            stage=CaseStage.REVIEWING, # Simplified for demo
            invoice_summary=invoice_summary,
            po_summary=po_summary,
            goods_receipt_summary=gr_summary,
            vendor_profile=vendor_profile,
            mismatch_flags=mismatch_flags,
            risk_flags=[], # Risk flags typically hidden until deep inspection
            requested_documents=self.state.pending_responses,
            days_until_due=case.get("days_until_due", 10),
            approval_threshold=case["policy"]["approval_threshold"],
            current_status=status,
            action_history=[a.action_type for a in self.state.actions_taken],
            remaining_steps=self.max_steps - self.state.elapsed_steps,
            notes_visible_to_agent=self._get_current_notes()
        )

    def _get_current_notes(self) -> str:
        if self.state.elapsed_steps == 0:
            return self._initial_notes
        if self.state.final_outcome:
            return f"Case finalized with outcome: {self.state.final_outcome}"
        
        last_action = self.state.actions_taken[-1] if self.state.actions_taken else None
        if not last_action:
            return self._initial_notes
            
        return f"Last action: {last_action.action_type}. Awaiting further processing."

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        self.state.elapsed_steps += 1
        self.state.actions_taken.append(action)
        
        reward = 0.0
        done = False
        info = {"action_feedback": ""}

        # Transition logic
        at = action.action_type
        
        if at == ActionType.INSPECT_INVOICE:
            if not self.state.revealed_info["invoice"]:
                reward += 0.1
                self.state.revealed_info["invoice"] = True
                info["action_feedback"] = "Invoice details visible."
            else:
                reward -= 0.05
                info["action_feedback"] = "Invoice already inspected."

        elif at == ActionType.INSPECT_PO:
          if not self.state.revealed_info["po"]:
                reward += 0.1
                self.state.revealed_info["po"] = True
                info["action_feedback"] = "PO details visible."
          else:
                reward -= 0.05

        elif at == ActionType.INSPECT_GOODS_RECEIPT:
            self.state.revealed_info["goods_receipt"] = True
            reward += 0.1

        elif at == ActionType.INSPECT_VENDOR_PROFILE:
            self.state.revealed_info["vendor_profile"] = True
            reward += 0.1

        elif at == ActionType.CHECK_DUPLICATE_INVOICE:
            self.state.is_duplicate_checked = True
            if "duplicate_invoice" in self.state.case_data.get("mismatches", []):
              reward += 0.2
              info["action_feedback"] = "Found duplicate invoice in history!"
            else:
              reward += 0.05

        elif at in [ActionType.APPROVE, ActionType.REJECT, ActionType.ESCALATE_MANAGER, ActionType.ESCALATE_RISK]:
            self.state.final_outcome = action.action_type.value
            done = True
            # Final reward handled by reward/grader logic
            info["action_feedback"] = f"Final decision: {self.state.final_outcome}"

        # Timeout
        if self.state.elapsed_steps >= self.max_steps:
            done = True
            info["action_feedback"] += " Max steps reached."

        obs = self._get_observation()
        return obs, reward, done, info
