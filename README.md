---
title: My OpenCV
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---
# ReconFlow-OpenEnv

**ReconFlow-OpenEnv** is a high-fidelity OpenEnv simulator for an Accounts Payable / Procurement Operations assistant. It simulates real-world invoice reconciliation workflows, business policy enforcement, and fraud risk detection.

This environment is designed for training and evaluating AI agents that automate business operations, specifically the matching of invoices against purchase orders (POs) and goods receipts (GRs).

---

## 🏛️ Domain Context
In modern finance operations, an agent (human or AI) must ensure the accuracy of outgoing payments. This process, known as **3-way matching**, involves verifying that:
1. The **Invoice** matches the **Purchase Order** (Intent).
2. The **Invoice** matches the **Goods Receipt** (Actual delivery).
3. The **Vendor** is legitimate and has no high-risk anomalies.

## 🚀 Key Features
- **Deterministic Simulation**: Built with structured scenario data (Easy, Medium, Hard).
- **OpenEnv Compliant**: Implements the standard `reset()`, `step(action)`, and `state()` API.
- **Rich Action Space**: Agents can inspect documents, compare values, check history, and escalate to humans.
- **Explainable Scoring**: Deterministic graders evaluate correctness, efficiency, and safety (0.0 to 1.0).
- **Reward Shaping**: Step-wise rewards for exploration and high penalties for unsafe approvals.

---

## 🛠️ Tech Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI (for API serving)
- **Validation**: Pydantic (for typed models)
- **Deployment**: Docker-ready, Hugging Face Space compatible.

---

## 📂 Project Structure
```
reconflow-openenv/
  app/
    main.py             # Server entrypoint
    api.py              # FastAPI endpoints
    env/
      environment.py    # OpenEnv implementation
      models.py         # Pydantic states, actions, obs
      scenarios.py      # Data loader
      rewards.py        # Reward logic
      graders.py        # Scoring logic
      state_machine.py  # Internal state transitions
  data/
    easy_cases.json     # Basic 3-way match
    medium_cases.json   # Policy-aware routing
    hard_cases.json     # Fraud/Anomaly detection
  tests/
    test_env.py         # Unit tests
  openenv.yaml          # OpenEnv manifest
  inference.py          # Baseline agent script
  Dockerfile            # Container setup
  requirements.txt      # Dependencies
```

---

## 📝 Usage

### Local Setup
1. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Environment Server**:
   ```bash
   python app/main.py
   ```
   The API will be available at `http://localhost:8000`.

3. **Run Baseline Inference**:
   ```bash
   python inference.py
   ```

4. **Run Tests**:
   ```bash
   PYTHONPATH=. python tests/test_env.py
   ```

### API Endpoints
- `POST /reset?task_id=easy`: Starts a new case. Returns `session_id` and initial `observation`.
- `POST /step/{session_id}`: Takes an action. Expects JSON: `{"action_type": "...", "reason": "..."}`.
- `GET /state/{session_id}`: Returns the full internal state (for debugging/grading).
- `GET /health`: Health check.

---

## 🧠 Environment Design

### 📦 Action Space
- `inspect_invoice`, `inspect_po`, `inspect_goods_receipt`, `inspect_vendor_profile`: Reveal hidden data.
- `check_duplicate_invoice`: Checks historical data for duplicates.
- `compare_amounts`, `compare_quantities`, `compare_tax`: Verifies alignment.
- `request_document`: Ask for missing data.
- `flag_mismatch`, `flag_fraud_risk`: Tag issues before action.
- **TERMINAL**: `approve`, `reject`, `escalate_manager`, `escalate_risk`.

### 📊 Observations
The observation is masked. Agents must perform `inspect` actions to see invoice totals, line items, or vendor history. This prevents trivial "magic" solutions and forces logical workflow progression.

### 🏆 Tasks & Difficulty
| Task | Level | Description | Core Challenge |
|---|---|---|---|
| **Task 1** | Easy | Basic 3-Way Match | Verify clean data or simple mismatch. |
| **Task 2** | Medium | Policy Compliance | Handle tax, duplicate checks, and thresholds. |
| **Task 3** | Hard | Fraud Escalation | Detect bank changes, price inflation, or split invoices. |

---

## ⚖️ Grading & Rewards
- **Grader (0.0 - 1.0)**: Combines Decision Accuracy (40%), Analysis Completeness (30%), Safety (20%), and Efficiency (10%).
- **Reward**:
  - `+0.1` per new document inspected.
  - `+0.5` for correct final decision.
  - `-1.0` for **Unsafe Approval** (approving a fraud-risk or high-mismatch case).

---

## 🐳 Docker Deployment
```bash
docker build -t reconflow .
docker run -p 8000:8000 reconflow
```

---
*Created for the OpenEnv Hackathon.*