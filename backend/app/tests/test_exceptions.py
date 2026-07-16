"""Unit tests for app.utils.exceptions."""

from app.utils.exceptions import (
    AppError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
    UpstreamServiceError,
    ValidationError,
)


def test_app_error_to_dict_shape():
    err = AppError("something broke", details={"field": "value"})
    result = err.to_dict()
    assert result == {
        "error": {
            "code": "internal_error",
            "message": "something broke",
            "details": {"field": "value"},
        }
    }


def test_not_found_error_status_and_code():
    err = NotFoundError("missing")
    assert err.status_code == 404
    assert err.error_code == "not_found"


def test_validation_error_status_and_code():
    err = ValidationError("bad input")
    assert err.status_code == 422
    assert err.error_code == "validation_error"


def test_unauthorized_error_status_and_code():
    err = UnauthorizedError("no token")
    assert err.status_code == 401


def test_forbidden_error_status_and_code():
    err = ForbiddenError("nope")
    assert err.status_code == 403


def test_rate_limit_error_status_and_code():
    err = RateLimitError("slow down")
    assert err.status_code == 429


def test_upstream_service_error_status_and_code():
    err = UpstreamServiceError("ollama down")
    assert err.status_code == 502


def test_details_default_to_empty_dict():
    err = AppError("no details given")
    assert err.details == {}
