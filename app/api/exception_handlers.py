from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    ResourceNotFoundError,
    RuleLimitExceededError,
)


def email_already_registered_handler(
    request: Request,
    exc: EmailAlreadyRegisteredError,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "CONFLICT",
                "message": exc.message,
            }
        },
    )


def invalid_credentials_handler(
    request: Request,
    exc: InvalidCredentialsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={
            "error": {
                "code": "INVALID_CREDENTIALS",
                "message": exc.message,
            }
        },
    )


def resource_not_found_handler(
    request: Request,
    exc: ResourceNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": exc.message,
            }
        },
    )

def rule_limit_exceeded_handler(
    request: Request,
    exc: RuleLimitExceededError,
) -> JSONResponse:

    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "RULE_LIMIT_EXCEEDED",
                "message": exc.message,
            }
        },
    )
