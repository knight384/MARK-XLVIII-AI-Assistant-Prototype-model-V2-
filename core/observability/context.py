import contextvars
import uuid
from typing import Dict, Any, Optional

# Context variables for correlation IDs
_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")
_request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")
_session_id: contextvars.ContextVar[str] = contextvars.ContextVar("session_id", default="")
_device_id: contextvars.ContextVar[str] = contextvars.ContextVar("device_id", default="")
_workflow_id: contextvars.ContextVar[str] = contextvars.ContextVar("workflow_id", default="")

class TraceContext:
    """Provides methods for managing propagation of correlation IDs."""
    
    @staticmethod
    def initialize(
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        device_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Initialize correlation variables, generating a new trace_id if none exists."""
        if not trace_id:
            trace_id = str(uuid.uuid4())
            
        _trace_id.set(trace_id)
        if request_id:
            _request_id.set(request_id)
        if session_id:
            _session_id.set(session_id)
        if device_id:
            _device_id.set(device_id)
        if workflow_id:
            _workflow_id.set(workflow_id)
            
        return TraceContext.get_context_dict()

    @staticmethod
    def get_context_dict() -> Dict[str, str]:
        """Returns the current trace context as a dictionary."""
        ctx = {}
        if tid := _trace_id.get():
            ctx["trace_id"] = tid
        if rid := _request_id.get():
            ctx["request_id"] = rid
        if sid := _session_id.get():
            ctx["session_id"] = sid
        if did := _device_id.get():
            ctx["device_id"] = did
        if wid := _workflow_id.get():
            ctx["workflow_id"] = wid
        return ctx

    @staticmethod
    def clear():
        """Clear context variables for the current context."""
        _trace_id.set("")
        _request_id.set("")
        _session_id.set("")
        _device_id.set("")
        _workflow_id.set("")
