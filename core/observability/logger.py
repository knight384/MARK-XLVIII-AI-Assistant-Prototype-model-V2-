import json
import logging
from typing import Any, Dict

from core.observability.context import TraceContext
from core.logging_setup import _sensitive_filter

class StructuredFormatter(logging.Formatter):
    """Formats log records as structured JSON, embedding TraceContext and kwargs."""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.default_kwargs = kwargs

    def format(self, record: logging.LogRecord) -> str:
        import datetime
        dt = datetime.datetime.fromtimestamp(record.created)
        # Base structured fields
        log_obj: Dict[str, Any] = {
            "timestamp": dt.isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add trace context
        log_obj.update(TraceContext.get_context_dict())

        # Include default kwargs
        log_obj.update(self.default_kwargs)

        # Include any extra kwargs passed to logger (e.g. `logger.info("msg", extra={"duration_ms": 10})`)
        if hasattr(record, "extra_fields"):
            log_obj.update(record.extra_fields)
        
        # Capture standard exception info if present
        if record.exc_info:
            log_obj["exc_info"] = self.formatException(record.exc_info)

        # Scrub sensitive data
        json_str = json.dumps(log_obj, default=str)
        
        # Use existing SensitiveDataFilter to redact from the JSON string itself.
        # This is safe because _sensitive_filter scrubs the formatted string.
        # However, to avoid parsing/re-parsing, we manually apply redaction logic to the JSON string.
        redacted = json_str
        for secret in _sensitive_filter._known_secrets:
            if secret and secret in redacted:
                redacted = redacted.replace(secret, "***REDACTED***")
        
        from core.logging_setup import _SECRET_PATTERNS
        for pattern in _SECRET_PATTERNS:
            redacted = pattern.sub(lambda m: m.group(1) + "***REDACTED***", redacted)

        return redacted

class StructuredLogger(logging.Logger):
    """Custom logger that wraps kwargs into an 'extra_fields' attribute for the formatter."""
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1, **kwargs):
        if kwargs:
            extra = extra or {}
            extra["extra_fields"] = kwargs
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

def configure_structured_logging(level: int = logging.INFO):
    """Upgrades root logger to use structured JSON logging."""
    logging.setLoggerClass(StructuredLogger)
    root = logging.getLogger()
    
    # We find existing handlers and swap their formatters
    formatter = StructuredFormatter()
    for handler in root.handlers:
        handler.setFormatter(formatter)
