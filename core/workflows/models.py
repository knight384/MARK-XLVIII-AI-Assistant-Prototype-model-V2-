import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class WorkflowState(str, Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    TIMEOUT = "TIMEOUT"

class StepState(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
    SKIPPED = "SKIPPED"

class EventType(str, Enum):
    WORKFLOW_CREATED = "WorkflowCreated"
    WORKFLOW_STARTED = "WorkflowStarted"
    STEP_QUEUED = "WorkflowStepQueued"
    STEP_STARTED = "WorkflowStepStarted"
    STEP_COMPLETED = "WorkflowStepCompleted"
    STEP_FAILED = "WorkflowStepFailed"
    WORKFLOW_WAITING = "WorkflowWaiting"
    WORKFLOW_RESUMED = "WorkflowResumed"
    RETRY_SCHEDULED = "WorkflowRetryScheduled"
    WORKFLOW_PAUSED = "WorkflowPaused"
    WORKFLOW_CANCELLED = "WorkflowCancelled"
    WORKFLOW_COMPLETED = "WorkflowCompleted"
    WORKFLOW_FAILED = "WorkflowFailed"
    WORKFLOW_TIMEOUT = "WorkflowTimeout"

class NodeType(str, Enum):
    AGENT = "AGENT"
    TOOL = "TOOL"
    CONDITION = "CONDITION"
    WAIT = "WAIT"
    NOTIFICATION = "NOTIFICATION"

class RetryPolicy(BaseModel):
    max_attempts: int = 0
    delay_seconds: float = 0.0
    exponential_backoff: bool = False
    max_backoff_seconds: float = 3600.0
    retryable_errors: List[str] = Field(default_factory=list)
    
class WorkflowStepConfig(BaseModel):
    node_type: NodeType
    config: Dict[str, Any] = Field(default_factory=dict)
    retry_policy: Optional[RetryPolicy] = None
    timeout_seconds: Optional[float] = None

class WorkflowStepDef(BaseModel):
    step_id: str
    name: str
    description: str = ""
    dependencies: List[str] = Field(default_factory=list)
    configuration: WorkflowStepConfig
    
class WorkflowDefinition(BaseModel):
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1
    name: str
    description: str = ""
    enabled: bool = True
    triggers: List[Dict[str, Any]] = Field(default_factory=list)
    steps: List[WorkflowStepDef] = Field(default_factory=list)
    inputs_schema: Dict[str, Any] = Field(default_factory=dict)
    outputs_schema: Dict[str, Any] = Field(default_factory=dict)
    retry_policy: Optional[RetryPolicy] = None
    timeout_seconds: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    owner: str = "system"

class WorkflowStepRun(BaseModel):
    step_run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_run_id: str
    step_id: str
    state: StepState = StepState.PENDING
    attempt: int = 0
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class WorkflowRun(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    state: WorkflowState = WorkflowState.READY
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    context: Dict[str, Any] = Field(default_factory=dict)

class WorkflowEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_run_id: str
    step_run_id: Optional[str] = None
    event_type: EventType
    timestamp: float = Field(default_factory=time.time)
    source: str = "system"
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
