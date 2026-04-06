from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any, Optional, List
from .env.environment import ReconFlowEnv
from .env.models import Action, Observation, StepResult, InternalState, ActionType, CaseStage
import uuid

app = FastAPI(title="ReconFlow-OpenEnv API", description="AI agent environment for invoice reconciliation.")

# Global environment instances (in-memory for simple demo)
envs: Dict[str, ReconFlowEnv] = {}

from pydantic import BaseModel
class ResetRequest(BaseModel):
    task_id: str = "easy"
    case_id: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok", "env": "ReconFlow-OpenEnv"}

@app.post("/reset")
def reset(task_id: str = "easy", case_id: Optional[str] = None):
    session_id = str(uuid.uuid4())
    env = ReconFlowEnv(task_id=task_id, case_id=case_id)
    obs = env.reset()
    envs[session_id] = env
    return {"session_id": session_id, "observation": obs.dict()}

@app.post("/step/{session_id}")
def step(session_id: str, action: Action):
    if session_id not in envs:
        raise HTTPException(status_code=404, detail="Session not found")
    
    env = envs[session_id]
    obs, reward, done, info = env.step(action)
    
    # Store session or delete if done? 
    # For this demo, let's keep it until explicit clear or timeout (not implemented).
    
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state/{session_id}")
def state(session_id: str):
    if session_id not in envs:
        raise HTTPException(status_code=404, detail="Session not found")
    return envs[session_id].state().dict()

@app.get("/tasks")
def list_tasks():
    manager = ReconFlowEnv().scenario_manager
    return {"tasks": manager.list_tasks()}

@app.get("/cases/{task_id}")
def list_cases(task_id: str):
    manager = ReconFlowEnv().scenario_manager
    return {"task_id": task_id, "cases": manager.list_cases(task_id)}
