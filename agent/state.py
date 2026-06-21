from typing import TypedDict, Sequence, Annotated, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class SupervisorState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
class BillingResult(BaseModel):
    domain: Literal["billing"]
    issue_type: Literal[
        "duplicate_charge",
        "refund",
        "subscription_charge",
        "payment_failed",
        "invoice_question",
        "unknown"
    ]
    confidence: float = Field(ge=0, le=1)
    answer: str
    missing_info: list[str]
    needs_escalation: bool
    escalation_reason: str | None = None
    
    
    
class TechnicalResult(BaseModel):
    domain: Literal["technical"]
    issue_type: Literal[
        "bug",
        "api_issue",
        "failed_workflow",
        "integrations",
        "performance_problem",
        "login_issue",
        "setup_issue",
        "unknown"
    ]
    confidence: float = Field(ge=0, le=1)
    answer: str
    missing_info: list[str]
    needs_escalation: bool
    escalation_reason: str | None = None
    
class EscalationResult(BaseModel):
    domain: Literal["escalation"]
    issue_type: Literal[
        "security",
        "financial_exception",
        "chargeback",
        "suspected_fraud",
        "account_lockout",
        "production_outage",
        "data_loss",
        "repeated_failed_resolution",
        "missing_authority_to_act",
        "unknown"
    ]
    confidence: float = Field(ge=0, le=1)
    summary: str
    reason: str
    priority: Literal["low", "normal", "high", "urgent"]
    
    
    
class FAQResult(BaseModel):
    domain: Literal["faq"]
    issue_type: Literal[
        "payment_methods",
        "billing_address",
        "billing_cycle",
        "subscription_cancellation",
        "refund_policy",
        "account_setup",
        "api_docs",
        "system_requirements",
        "data_export",
        "security",
        "password_reset",
        "integrations",
        "general_policy",
        "unknown"
    ]
    answer: str
    confidence: float = Field(ge=0, le=1)
    source: str | None
    missing_info: list[str]
    needs_escalation: bool
    escalation_reason: str | None = None
    
