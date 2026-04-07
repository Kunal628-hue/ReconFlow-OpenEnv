from typing import Dict, Any, Tuple, Optional
from .scenarios import ScenarioManager
from .state_machine import ReconFlowStateMachine
from .models import (
    Action, Observation, StepResult, InternalState
)
from .graders import ReconFlowGrader
from .rewards import RewardCalculator

from .rewards import RewardCalculator

class ReconFlowEnv:
    def __init__(self, task_id: str = "easy", case_id: Optional[str] = None):
        self.scenario_manager = ScenarioManager()
        self.task_id = task_id
        self.case_id = case_id
        self.scenario = self.scenario_manager.get_scenario(task_id, case_id) or {}
        self.state_machine = ReconFlowStateMachine(self.scenario)
        self.grader = ReconFlowGrader(self.scenario)
        self.reward_calculator = RewardCalculator(self.scenario)

    def reset(self) -> Observation:
        return self.state_machine.reset()

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        obs, reward, done, info = self.state_machine.step(action)
        
        # Calculate complex rewards if needed (optional)
        # For this version, step() from state_machine is enough, 
        # but final reward is added when done
        if done:
            final_reward = self.reward_calculator.calculate_final_reward(self.state_machine.state)
            reward += final_reward
            info["final_score"] = self.grader.grade(self.state_machine.state)
            info["score_explanation"] = self.grader.explain_score(self.state_machine.state)
        
        return obs, max(0.01, min(0.99, float(reward))), done, info

    def state(self) -> InternalState:
        return self.state_machine.state

    def list_tasks(self) -> list:
        return self.scenario_manager.list_tasks()

    def list_cases(self, task_id: str) -> list:
        return self.scenario_manager.list_cases(task_id)
