from fastapi import FastAPI

from app.api.routes.tasks import router as tasks_router

from app.api.exception_handlers import (
    email_already_registered_handler,
    invalid_credentials_handler,
    resource_not_found_handler,
)
from app.api.routes.auth import router as auth_router
from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    ResourceNotFoundError,
)
from app.api.routes.rules import router as rules_router


app = FastAPI()


app.add_exception_handler(
    EmailAlreadyRegisteredError,
    email_already_registered_handler,
)

app.add_exception_handler(
    InvalidCredentialsError,
    invalid_credentials_handler,
)

app.add_exception_handler(
    ResourceNotFoundError,
    resource_not_found_handler,
)


app.include_router(
    auth_router,
    prefix="/api",
)

app.include_router(
    tasks_router,
    prefix="/api",
)

app.include_router(
    rules_router,
    prefix="/api",
)