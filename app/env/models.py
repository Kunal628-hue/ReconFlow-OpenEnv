from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    INSPECT_INVOICE = "inspect_invoice"
    INSPECT_PO = "inspect_po"
    INSPECT_GOODS_RECEIPT = "inspect_goods_receipt"
    INSPECT_VENDOR_PROFILE = "inspect_vendor_profile"
    COMPARE_AMOUNTS = "compare_amounts"
    COMPARE_QUANTITIES = "compare_quantities"
    COMPARE_TAX = "compare_tax"
    CHECK_DUPLICATE_INVOICE = "check_duplicate_invoice"
    REQUEST_DOCUMENT = "request_document"
    FLAG_MISMATCH = "flag_mismatch"
    FLAG_FRAUD_RISK = "flag_fraud_risk"
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE_MANAGER = "escalate_manager"
    ESCALATE_RISK = "escalate_risk"
    WAIT = "wait"

class Action(BaseModel):
    action_type: ActionType
    target_field: Optional[str] = None
    target_document: Optional[str] = None
    reason: Optional[str] = None
    decision: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class MismatchFlag(str, Enum):
    AMOUNT_MISMATCH = "amount_mismatch"
    QUANTITY_MISMATCH = "quantity_mismatch"
    TAX_MISMATCH = "tax_mismatch"
    MISSING_DOC = "missing_document"
    DUPLICATE_INVOICE = "duplicate_invoice"
    INVALID_VENDOR = "invalid_vendor"
    UNAUTHORIZED_PURCHASE = "unauthorized_purchase"

class RiskFlag(str, Enum):
    BANK_ACCOUNT_CHANGE = "bank_account_change"
    UNUSUAL_PRICE_INFLATION = "unusual_price_inflation"
    SPLIT_INVOICE = "split_invoice"
    NEGATIVE_VENDOR_HISTORY = "negative_vendor_history"
    INCONSISTENT_DELIVERY = "inconsistent_delivery"

class CaseStage(str, Enum):
    INITIAL = "initial"
    REVIEWING = "reviewing"
    COMPARING = "comparing"
    DONE = "done"

class Observation(BaseModel):
    case_id: str
    task_id: str
    stage: CaseStage
    invoice_summary: Optional[Dict[str, Any]] = None
    po_summary: Optional[Dict[str, Any]] = None
    goods_receipt_summary: Optional[Dict[str, Any]] = None
    vendor_profile: Optional[Dict[str, Any]] = None
    mismatch_flags: List[MismatchFlag] = Field(default_factory=list)
    risk_flags: List[RiskFlag] = Field(default_factory=list)
    requested_documents: List[str] = Field(default_factory=list)
    days_until_due: int
    approval_threshold: float
    current_status: str
    action_history: List[str] = Field(default_factory=list)
    remaining_steps: int
    notes_visible_to_agent: str

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]

class InternalState(BaseModel):
    case_data: Dict[str, Any]
    revealed_info: Dict[str, bool] = Field(default_factory=lambda: {
        "invoice": False,
        "po": False,
        "goods_receipt": False,
        "vendor_profile": False
    })
    actions_taken: List[Action] = Field(default_factory=list)
    resolved_mismatches: List[str] = Field(default_factory=list)
    is_duplicate_checked: bool = False
    is_vendor_history_checked: bool = False
    is_missing_docs_requested: bool = False
    pending_responses: List[str] = Field(default_factory=list)
    elapsed_steps: int = 0
    final_outcome: Optional[str] = None
    cumulative_reward: float = 0.0
