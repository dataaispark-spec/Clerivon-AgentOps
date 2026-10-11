from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def now_utc() -> datetime:
    return datetime.now(UTC)


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class WorkflowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: str = Field(min_length=1, max_length=100)
    case_id: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: make_id("ev"))
    source: str
    description: str
    observed_at: datetime | None = None
    freshness: str = "unknown"
    attributes: dict[str, Any] = Field(default_factory=dict)


class WorkflowResult(BaseModel):
    workflow_id: str = Field(default_factory=lambda: make_id("wf"))
    tenant_id: str
    vertical: str
    status: str
    summary: str
    recommendation: dict[str, Any]
    evidence: list[Evidence] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    requires_human_approval: bool = True
    created_at: datetime = Field(default_factory=now_utc)


class ProposalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: str = Field(min_length=1, max_length=100)
    vertical: str
    action_type: str
    target_id: str
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: str
    proposal_id: str
    approver_id: str
    decision: str
    comment: str = ""


class ExecuteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenant_id: str
    proposal_id: str
    idempotency_key: str = Field(min_length=8, max_length=200)
