"""
Application-wide exception hierarchy.

Using typed exceptions instead of raising raw HTTPException everywhere lets
services and agents stay framework-agnostic (they don't need to import
FastAPI), while the global exception handlers in app.main translate these
into consistent JSON error responses.
"""

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base class for all application-raised errors."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"


class UnauthorizedError(AppError):
    status_code = 401
    error_code = "unauthorized"


class ForbiddenError(AppError):
    status_code = 403
    error_code = "forbidden"


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"


class RateLimitError(AppError):
    status_code = 429
    error_code = "rate_limited"


class UpstreamServiceError(AppError):
    """Raised when Ollama, ChromaDB, MongoDB, or Firebase calls fail."""

    status_code = 502
    error_code = "upstream_service_error"


class FileProcessingError(AppError):
    status_code = 422
    error_code = "file_processing_error"
