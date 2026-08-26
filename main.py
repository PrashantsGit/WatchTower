from fastapi import FastAPI

from app.monitoring.engine import MonitoringEngineService
from app.scheduler.runner import SchedulerRunner

from app.api.routes.tasks import router as tasks_router

from app.api.exception_handlers import (
    email_already_registered_handler,
    invalid_credentials_handler,
    resource_not_found_handler,
    rule_limit_exceeded_handler,
)
from app.api.routes.auth import router as auth_router
from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    ResourceNotFoundError,
    RuleLimitExceededError,
)
from app.api.routes.rules import router as rules_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_exception_handler(
    EmailAlreadyRegisteredError,
    email_already_registered_handler,
)
app.add_exception_handler(
    RuleLimitExceededError,
    rule_limit_exceeded_handler,
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)