class ScaleSafeException(Exception):
    """Base exception class for ScaleSafe errors."""

    pass


class ScaleSafeTokenError(ScaleSafeException):
    """Exception for issues with the ScaleSafe API Key."""

    def __init__(
        self,
        message="Something looks wrong with your ScaleSafe API Key. Check your object's api_key variable or on your account at app.scalesafe.ai.",
    ):
        super().__init__(message)


class OutOfComplianceError(ScaleSafeException):
    """Exception raised for operations violating compliance rules."""

    pass


class HumanStoppedTheLoopError(OutOfComplianceError):
    """Raised when human intervention stops a loop or process."""

    def __init__(self, message="A human intervention has stopped the loop or process."):
        super().__init__(message)


class UnsafeInputError(OutOfComplianceError):
    """Raised for inputs deemed unsafe or risky."""

    def __init__(self, message="The input has been deemed unsafe or risky."):
        super().__init__(message)


class BannedOutputError(OutOfComplianceError):
    """Raised when an output is banned or not allowed."""

    def __init__(self, message="This output is banned or not allowed."):
        super().__init__(message)


class BannedLocationError(OutOfComplianceError):
    """Raised when a location is banned or not allowed for operations."""

    def __init__(
        self, message="This location is banned or not allowed for operations."
    ):
        super().__init__(message)


class ConfigurationError(OutOfComplianceError):
    """Raised for issues related to configuration settings."""

    def __init__(self, message="There are issues related to configuration settings."):
        super().__init__(message)


class HumanReviewNeededException(ScaleSafeException):
    """Raised when human review is needed for a process."""

    def __init__(self, message="Human review is needed for this process."):
        super().__init__(message)


class APIRateLimitExceededError(ScaleSafeException):
    """Exception raised when the API call limit is exceeded."""

    def __init__(
        self,
        message="API rate limit has been exceeded. Please wait before making more requests.",
    ):
        super().__init__(message)


class DataValidationError(ScaleSafeException):
    """Exception raised for data validation errors."""

    def __init__(
        self,
        message="Data validation error: missing or incorrect fields. Please ensure all required fields are correctly formatted.",
    ):
        super().__init__(message)


class DatabaseOperationError(ScaleSafeException):
    """Exception raised for Firestore operation failures."""

    def __init__(
        self,
        message="A database operation failed. Please try again or contact support if the issue persists.",
    ):
        super().__init__(message)


class UnauthorizedAccessError(ScaleSafeException):
    """Exception raised for unauthorized access attempts."""

    def __init__(
        self,
        message="Unauthorized access attempt detected. Ensure you have the correct permissions.",
    ):
        super().__init__(message)


class ResourceNotFoundError(ScaleSafeException):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self,
        message="The requested resource was not found. Verify the resource ID or contact support if the issue persists.",
    ):
        super().__init__(message)
