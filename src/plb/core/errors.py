class PLBError(Exception):
    """Base error for plb."""


class WorkflowStateError(PLBError):
    """Raised when workflow state is inconsistent."""


class CommandNotImplementedError(PLBError):
    """Raised when a scaffolded command has no real implementation yet."""

