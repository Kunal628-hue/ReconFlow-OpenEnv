import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.env.environment import ReconFlowEnv
from app.env.models import Action, ActionType, CaseStage

def test_easy_approval():
    env = ReconFlowEnv(task_id="easy", case_id="easy-001")
    obs = env.reset()
    assert obs.case_id == "easy-001"
    
    # 1. Inspect Invoice
    obs, reward, done, info = env.step(Action(action_type=ActionType.INSPECT_INVOICE))
    assert obs.invoice_summary is not None
    assert reward > 0
    
    # 2. Inspect PO
    obs, reward, done, info = env.step(Action(action_type=ActionType.INSPECT_PO))
    assert obs.po_summary is not None
    
    # 3. Final Decision - Approve
    obs, reward, done, info = env.step(Action(action_type=ActionType.APPROVE))
    assert done
    assert info["final_score"] >= 0.8

def test_med_threshold_escalation():
    env = ReconFlowEnv(task_id="medium", case_id="med-001")
    env.reset()
    
    # Decision directly
    obs, reward, done, info = env.step(Action(action_type=ActionType.ESCALATE_MANAGER))
    assert done
    assert reward >= 0 # Correct resolution for high amount case
    assert info["score_explanation"]["final_outcome"] == "escalate_manager"

def test_step_limit():
    env = ReconFlowEnv(task_id="easy", case_id="easy-001")
    env.reset()
    for _ in range(15):
        obs, reward, done, info = env.step(Action(action_type=ActionType.WAIT))
    assert done
    assert "Max steps reached" in info["action_feedback"]

if __name__ == "__main__":
    print("Running tests...")
    try:
        test_easy_approval()
        test_med_threshold_escalation()
        test_step_limit()
        print("ALL TESTS PASSED!")
    except Exception as e:
        print(f"TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
