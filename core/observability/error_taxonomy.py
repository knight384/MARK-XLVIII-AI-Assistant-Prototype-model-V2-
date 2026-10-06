from enum import Enum
from typing import Optional

class ErrorCategory(str, Enum):
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    APPROVAL_REQUIRED = "approval_required"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    TIMEOUT = "timeout"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    DATABASE_ERROR = "database_error"
    WORKFLOW_ERROR = "workflow_error"
    TOOL_ERROR = "tool_error"
    SANDBOX_ERROR = "sandbox_error"
    SIDECAR_ERROR = "sidecar_error"
    PROVIDER_ERROR = "provider_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    INTERNAL_ERROR = "internal_error"

class V2Error(Exception):
    """Base class for all internal V2 operational errors."""
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        code: str,
        is_retryable: bool = False,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.code = code
        self.is_retryable = is_retryable
        self.original_exception = original_exception

    def to_dict(self) -> dict:
        return {
            "error_code": self.code,
            "category": self.category.value,
            "message": self.message,
            "retryable": self.is_retryable,
        }

# Example specific errors
class DependencyUnavailableError(V2Error):
    def __init__(self, message: str, component: str):
        super().__init__(
            message=message,
            category=ErrorCategory.DEPENDENCY_UNAVAILABLE,
            code=f"ERR_DEP_UNAVAILABLE_{component.upper()}",
            is_retryable=True
        )

class DatabaseContentionError(V2Error):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE_ERROR,
            code="ERR_DB_CONTENTION",
            is_retryable=True
        )

class AuthorizationError(V2Error):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            category=ErrorCategory.AUTHORIZATION_ERROR,
            code="ERR_AUTHZ_DENIED",
            is_retryable=False
        )
