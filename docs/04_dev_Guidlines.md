# WatchTower

# Development Guidelines

---

**Document Version:** 1.0

**Document Status:** Draft

**Prepared By:** Team WatchTower

**Related Documents:**

- Software Requirements Specification (SRS)
- Software Architecture Design (SAD)
- Database Design Document (DDD)

---

# 1. Introduction

## Chapter Overview

This document defines the development standards and practices to be followed during the implementation of WatchTower.

The guidelines establish a consistent approach to project structure, coding, error handling, testing, version control, configuration management, and day-to-day development.

The purpose is not to impose unnecessary restrictions on implementation, but to ensure that the codebase remains readable, maintainable, and consistent as WatchTower grows.

---

## 1.1 Purpose

The purpose of this document is to:

- Establish consistent development practices.
- Define project and code organization.
- Reduce unnecessary implementation differences.
- Improve code readability and maintainability.
- Establish a consistent Git workflow.
- Define basic testing and error-handling practices.
- Provide development guidance for future contributors.

---

## 1.2 Scope

These guidelines cover:

- Project structure
- Coding standards
- Naming conventions
- Error handling
- Logging
- Testing
- Git and version control
- Environment configuration
- Development workflow

Detailed system architecture and database design are documented separately in the SAD and DDD.

---

## 1.3 Development Philosophy

WatchTower development follows the following principles:

### Keep It Simple

Prefer simple and understandable solutions over unnecessary complexity.

### Follow the Architecture

Implementation shall follow the layered architecture and component boundaries defined in the SAD.

### Avoid Duplication

Common functionality should be implemented once and reused where appropriate.

### Design for Extension

New functionality should use existing extension points whenever possible.

### Document Meaningful Decisions

Important architectural or implementation decisions should be documented rather than left implicit.

---

## Chapter Summary

This chapter establishes the purpose, scope, and development philosophy of the WatchTower project. The following chapters define the practical standards used during implementation.

# 2. Project Structure

---

## Chapter Overview

This chapter defines the recommended project structure for the WatchTower backend.

The structure follows the layered architecture established in the Software Architecture Design (SAD) while keeping individual components organized by responsibility.

The project structure is designed to make the codebase easy to navigate without introducing unnecessary folder or module complexity.

---

## 2.1 Root Project Structure

The initial backend structure shall follow the organization below:

```text
watchtower/
│
├── app/
│   │
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   │
│   ├── database/
│   │   ├── session.py
│   │   ├── base.py
│   │   └── migrations/
│   │
│   ├── models/
│   │
│   ├── schemas/
│   │
│   ├── repositories/
│   │
│   ├── services/
│   │
│   ├── monitoring/
│   │
│   ├── notifications/
│   │
│   └── scheduler/
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── main.py
```

---

## 2.2 Directory Responsibilities

| Directory | Responsibility |
|-----------|----------------|
| `app/api/` | API routes, dependencies, and HTTP-related functionality. |
| `app/core/` | Application configuration, security, and shared infrastructure. |
| `app/database/` | Database connection, SQLAlchemy configuration, and migrations. |
| `app/models/` | SQLAlchemy ORM models. |
| `app/schemas/` | Pydantic request and response schemas. |
| `app/repositories/` | Database access and persistence operations. |
| `app/services/` | Business logic and application workflows. |
| `app/monitoring/` | Monitoring engine and monitoring-related components. |
| `app/notifications/` | Notification generation and delivery components. |
| `app/scheduler/` | Background scheduling and task execution. |
| `tests/` | Automated test suites. |

---

## 2.3 Layer Responsibility

The project structure reflects the following dependency direction:

```mermaid
flowchart TB

API[API Layer]

SERVICES[Service Layer]

REPOSITORIES[Repository Layer]

DATABASE[(Database)]

API --> SERVICES

SERVICES --> REPOSITORIES

REPOSITORIES --> DATABASE
```

Supporting components such as monitoring, notifications, and scheduling interact with the appropriate service and infrastructure layers without bypassing architectural boundaries.

---

## 2.4 Module Organization

Modules should be organized according to responsibility rather than individual endpoints.

For example:

```text
app/
│
├── api/
│   └── routes/
│       ├── auth.py
│       ├── monitoring.py
│       ├── history.py
│       └── notifications.py
│
├── services/
│   ├── auth_service.py
│   ├── monitoring_service.py
│   └── notification_service.py
│
└── repositories/
    ├── user_repository.py
    ├── monitoring_repository.py
    └── notification_repository.py
```

This prevents business logic from becoming scattered across individual route handlers.

---

## 2.5 File Organization Principles

The following principles shall be followed:

- Keep modules focused on a single responsibility.
- Avoid excessively large files.
- Group related functionality together.
- Keep API routes thin.
- Keep business logic within services.
- Keep database operations within repositories.
- Avoid circular dependencies between layers.
- Introduce new directories only when they provide a meaningful separation of responsibility.

---

## 2.6 Growth Strategy

The initial project structure should remain simple.

As WatchTower grows, modules may be further divided when:

- A module becomes difficult to maintain.
- A domain gains multiple independent components.
- A clear architectural boundary emerges.
- Testing becomes easier through separation.

New structure should be introduced based on actual project needs rather than speculative future requirements.

---

## Chapter Summary

This chapter established the physical organization of the WatchTower codebase and mapped project directories to their architectural responsibilities.

The structure provides a clear separation between API handling, business logic, persistence, monitoring, scheduling, and notifications while allowing the project to grow without unnecessary complexity.

# 3. Coding Standards

---

## Chapter Overview

This chapter defines the coding standards to be followed during WatchTower development.

The purpose of these standards is to keep the codebase readable, predictable, and maintainable without introducing unnecessary restrictions or development overhead.

The guidelines primarily apply to Python, FastAPI, SQLAlchemy, and Pydantic code used within the project.

---

## 3.1 General Python Standards

WatchTower shall follow standard Python conventions wherever practical.

The following principles shall be followed:

- Use **PEP 8** as the general coding style reference.
- Use meaningful and descriptive names.
- Prefer readable code over unnecessarily compact code.
- Keep functions focused on a single responsibility.
- Avoid unnecessary global state.
- Avoid duplicated logic.
- Use explicit imports rather than wildcard imports.

---

## 3.2 Naming Conventions

Python naming shall follow standard conventions.

| Element | Convention | Example |
|---------|------------|---------|
| Variables | `snake_case` | `target_url` |
| Functions | `snake_case` | `create_task()` |
| Classes | `PascalCase` | `MonitoringTask` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_INTERVAL` |
| Private members | Leading underscore | `_validate_rule()` |
| Modules | `snake_case` | `monitoring_service.py` |

Names should describe the purpose of the element rather than its implementation details.

---

## 3.3 Type Hints

Type hints should be used throughout the application wherever they improve clarity.

Example:

```python
def get_task(task_id: int) -> MonitoringTask:
    ...
```

For functions that do not return a value:

```python
def delete_task(task_id: int) -> None:
    ...
```

Type hints are particularly encouraged for:

- Service methods
- Repository methods
- API functions
- Configuration objects
- Complex data structures

---

## 3.4 Function Design

Functions should remain focused and reasonably sized.

A function should generally:

- Perform one logical responsibility.
- Have clear inputs and outputs.
- Avoid modifying unrelated application state.
- Raise meaningful exceptions when necessary.

Large functions should be divided when doing so improves readability or testability.

However, functions shall not be split artificially simply to satisfy a fixed line count.

---

## 3.5 Class Design

Classes should represent a meaningful responsibility within the system.

Examples include:

```text
MonitoringService
MonitoringRepository
NotificationService
MonitoringEngine
```

Classes should avoid becoming collections of unrelated utility methods.

When a class becomes responsible for multiple independent concerns, its responsibilities should be reconsidered and separated where appropriate.

---

## 3.6 FastAPI Standards

API route handlers should remain thin.

A typical request flow should follow:

```text
API Route
    ↓
Service
    ↓
Repository
    ↓
Database
```

Route handlers should primarily be responsible for:

- Receiving requests.
- Validating request data.
- Calling the appropriate service.
- Returning the appropriate response.

Business logic should not be placed directly inside route handlers.

---

## 3.7 Pydantic Schemas

Pydantic schemas shall be used for API request and response validation.

Schemas should clearly distinguish between:

- Request models
- Response models
- Internal database models

Example:

```text
schemas/
├── user.py
├── monitoring.py
├── history.py
└── notification.py
```

Database ORM models should not be exposed directly as API contracts.

---

## 3.8 SQLAlchemy Standards

SQLAlchemy models shall follow the database structure defined in the DDD.

The following principles shall be followed:

- Table and column names shall match the DDD.
- Foreign key relationships shall be explicitly defined.
- Database constraints shall be represented where appropriate.
- ORM models shall remain focused on persistence representation.
- Business logic should not be placed inside database models unless it is directly related to model behavior.

---

## 3.9 Asynchronous Code

Asynchronous programming should be used where it provides a practical benefit.

Appropriate use cases include:

- FastAPI request handling.
- Network operations.
- Monitoring operations involving external resources.
- Notification delivery.
- Other I/O-bound operations.

CPU-intensive operations should not be made asynchronous merely for consistency.

The project should avoid mixing synchronous and asynchronous patterns unnecessarily.

---

## 3.10 Comments and Documentation

Comments should explain **why** something is done rather than simply repeating **what** the code does.

### Avoid

```python
# Increment counter by one
counter += 1
```

### Prefer

```python
# Prevent duplicate execution within the same scheduler cycle.
counter += 1
```

Documentation should be added when:

- A decision is non-obvious.
- A workaround is required.
- External behavior needs clarification.
- A complex algorithm needs explanation.

---

## 3.11 Docstrings

Docstrings should be used for public classes, services, and functions where their purpose or behavior is not immediately obvious.

Example:

```python
def detect_change(previous, current):
    """
    Compares two monitoring snapshots and determines
    whether a meaningful change has occurred.
    """
```

Simple private functions with self-explanatory names do not require excessive documentation.

---

## 3.12 Error Handling

Errors should be handled at the appropriate architectural layer.

```text
Database Error
      ↓
Repository
      ↓
Service
      ↓
API Exception Handler
      ↓
HTTP Response
```

The following principles shall apply:

- Do not silently ignore errors.
- Do not expose internal exceptions directly to API clients.
- Use meaningful application-level exceptions.
- Log unexpected failures.
- Return appropriate HTTP status codes from API endpoints.

---

## 3.13 Code Quality Principles

The following principles should guide implementation.

### Readability Over Cleverness

Prefer straightforward code that another developer can understand quickly.

### Explicit Over Implicit

Important behavior should be visible rather than hidden behind unnecessary abstractions.

### Reuse Over Duplication

Common logic should be centralized when reuse is meaningful.

### Simplicity Over Premature Optimization

Performance optimizations should be introduced when there is a demonstrated need.

### Architecture Over Convenience

Shortcuts that violate established architectural boundaries should be avoided even when they appear faster initially.

---

## Chapter Summary

This chapter established practical coding standards for WatchTower development.

The standards focus on readability, clear responsibilities, type safety, appropriate abstraction, and adherence to the architecture while deliberately avoiding unnecessary rules that could slow development.

# 4. Naming Conventions

---

## Chapter Overview

This chapter defines the naming conventions used throughout the WatchTower codebase.

Consistent naming improves readability, makes the project easier to navigate, and reduces ambiguity when working across different architectural layers.

The conventions in this chapter apply to Python modules, packages, classes, functions, variables, constants, API components, and other code-level elements.

Database naming conventions are defined separately in the Database Design Document (DDD).

---

## 4.1 General Naming Principles

The following principles shall be followed:

- Names should be descriptive and meaningful.
- Standard Python naming conventions should be preferred.
- Abbreviations should be avoided unless they are widely understood.
- Names should reflect the responsibility of the component.
- Similar concepts should use consistent terminology throughout the codebase.
- Database naming conventions shall follow the rules defined in the DDD.

---

## 4.2 Module and Package Naming

Python modules and packages shall use lowercase `snake_case` names.

### Examples

```text
monitoring_service.py
notification_service.py
user_repository.py
database.py
security.py
```

Packages should also use lowercase names.

```text
monitoring/
notifications/
repositories/
services/
```

---

## 4.3 Class Naming

Classes shall use `PascalCase`.

### Examples

```python
class MonitoringService:
    ...


class MonitoringRepository:
    ...


class NotificationService:
    ...
```

Class names should represent a meaningful entity, responsibility, or abstraction.

---

## 4.4 Function and Method Naming

Functions and methods shall use `snake_case`.

Names should generally begin with a verb when representing an action.

### Examples

```python
create_task()
get_task()
update_task()
delete_task()
detect_change()
send_notification()
```

Functions that retrieve information should use names such as:

```python
get_task()
get_user()
find_history_events()
```

Functions that modify state should use names such as:

```python
create_task()
update_task()
delete_task()
```

---

## 4.5 Variable Naming

Variables shall use descriptive `snake_case` names.

### Preferred

```python
target_url = task.target_url
check_interval = task.check_interval
next_execution_at = calculate_next_execution(...)
```

### Avoid

```python
url1 = task.target_url
ci = task.check_interval
x = calculate_next_execution(...)
```

Short names may be used when their meaning is immediately obvious within a small scope.

For example:

```python
for task in tasks:
    ...
```

---

## 4.6 Constant Naming

Constants shall use `UPPER_SNAKE_CASE`.

### Examples

```python
DEFAULT_CHECK_INTERVAL = 60
MAX_RETRY_ATTEMPTS = 3
DEFAULT_NOTIFICATION_TIMEOUT = 30
```

Constants should be defined centrally when they are shared across multiple modules.

---

## 4.7 Boolean Naming

Boolean variables, fields, and properties should use names that clearly communicate a true or false state.

Preferred prefixes include:

```text
is_
has_
can_
should_
```

### Examples

```python
is_active
is_verified
has_permission
can_retry
```

Avoid ambiguous names such as:

```python
active
status_flag
check
```

when a clearer boolean name is possible.

---

## 4.8 API Naming

API endpoint names should follow the resource-oriented conventions defined in the API Design Document.

Resources should generally use plural nouns.

### Examples

```text
/tasks
/users
/notifications
/history
```

Resource identifiers should be represented using path parameters.

Example:

```text
/tasks/{task_id}
```

HTTP methods should communicate the intended operation.

| Method | Purpose |
|--------|---------|
| GET | Retrieve resources |
| POST | Create resources |
| PUT | Replace or update resources |
| PATCH | Partially update resources |
| DELETE | Remove resources |

---

## 4.9 Schema Naming

Pydantic schemas shall use descriptive `PascalCase` names.

Request schemas should use the appropriate action suffix.

### Examples

```python
class UserCreate:
    ...


class UserLogin:
    ...


class MonitoringTaskCreate:
    ...


class MonitoringTaskUpdate:
    ...
```

Response schemas should use descriptive names.

```python
class MonitoringTaskResponse:
    ...


class HistoryEventResponse:
    ...


class NotificationResponse:
    ...
```

---

## 4.10 Repository Naming

Repository classes shall use the entity name followed by `Repository`.

### Examples

```python
UserRepository
MonitoringTaskRepository
MonitoringRuleRepository
HistoryEventRepository
NotificationRepository
```

Repository methods should describe the persistence operation being performed.

```python
create()
get_by_id()
get_by_user_id()
update()
delete()
```

---

## 4.11 Service Naming

Service classes shall use the primary responsibility followed by `Service`.

### Examples

```python
AuthService
MonitoringService
NotificationService
HistoryService
```

Service methods should describe business operations rather than database operations.

### Preferred

```python
create_monitoring_task()
evaluate_monitoring_rules()
process_detected_change()
send_notification()
```

### Avoid

```python
insert_task()
update_database()
execute_sql()
```

Database-specific terminology should remain within the repository layer.

---

## 4.12 Exception Naming

Custom exceptions shall use `PascalCase` and generally end with `Error`.

### Examples

```python
TaskNotFoundError
UnauthorizedError
MonitoringExecutionError
NotificationDeliveryError
```

Exceptions should communicate the type of failure clearly.

---

## 4.13 Test Naming

Test files should follow the module or feature being tested.

### Examples

```text
test_auth.py
test_monitoring.py
test_notifications.py
test_repositories.py
```

Test functions should describe the expected behavior.

```python
def test_create_monitoring_task():
    ...


def test_task_creation_requires_authenticated_user():
    ...


def test_failed_notification_is_recorded():
    ...
```

---

## 4.14 Naming Consistency

The same concept shall use the same terminology throughout the application.

For example, if the domain model uses:

```text
Monitoring Task
```

the code should consistently use:

```python
MonitoringTask
monitoring_task
monitoring_tasks
```

The project should avoid using different terms such as:

```text
Task
Monitor
MonitoringJob
Watch
```

for the same domain concept unless they represent genuinely different concepts.

---

## Chapter Summary

This chapter established code-level naming conventions for WatchTower.

Consistent naming across modules, classes, functions, variables, API resources, schemas, repositories, services, exceptions, and tests will make the codebase easier to understand and maintain while keeping terminology aligned with the system's domain model.

# 5. Error Handling

---

## Chapter Overview

This chapter defines the error-handling approach used throughout the WatchTower application.

The error-handling strategy is designed to provide predictable behavior, prevent sensitive implementation details from being exposed to users, and ensure that failures are properly recorded for debugging and maintenance.

Errors shall be handled at the architectural layer where they can be understood and appropriately translated.

---

## 5.1 Error Handling Principles

The following principles shall guide error handling throughout the application:

- Errors shall not be silently ignored.
- Exceptions should be handled at the appropriate layer.
- Internal implementation details shall not be exposed through API responses.
- Errors should provide enough information for debugging.
- Expected application errors should be distinguishable from unexpected system failures.
- Database transactions shall be rolled back when an operation fails.
- Unexpected failures shall be logged.

---

## 5.2 Error Flow

Errors should move through the application according to the following flow:

```text
External / Database / Application Error
                │
                ▼
       Repository / Service
                │
                ▼
       Application Exception
                │
                ▼
       API Exception Handler
                │
                ▼
          HTTP Response
```

The layer where an error originates should not necessarily be responsible for presenting the error to the user.

---

## 5.3 Application Exceptions

Application-specific exceptions should be used for expected business and application failures.

Examples include:

```python
class TaskNotFoundError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class MonitoringExecutionError(Exception):
    pass


class NotificationDeliveryError(Exception):
    pass
```

These exceptions allow the application to distinguish expected failures from unexpected programming or infrastructure errors.

---

## 5.4 API Error Responses

API errors shall use appropriate HTTP status codes.

| HTTP Status | Usage |
|-------------|-------|
| `400 Bad Request` | Invalid or malformed request. |
| `401 Unauthorized` | Authentication is missing or invalid. |
| `403 Forbidden` | User is authenticated but not permitted to perform the operation. |
| `404 Not Found` | Requested resource does not exist. |
| `409 Conflict` | Request conflicts with the current application state. |
| `422 Unprocessable Entity` | Request validation failed. |
| `500 Internal Server Error` | Unexpected server-side failure. |
| `503 Service Unavailable` | Required external or infrastructure service is temporarily unavailable. |

The exact status code shall depend on the nature of the failure.

---

## 5.5 Standard Error Response

API errors should follow a consistent response structure.

Example:

```json
{
    "error": {
        "code": "TASK_NOT_FOUND",
        "message": "The requested monitoring task was not found."
    }
}
```

The response should contain a user-safe message and, where useful, a stable application error code.

Internal exception messages, stack traces, SQL statements, credentials, or other sensitive implementation details shall not be returned to API clients.

---

## 5.6 Validation Errors

Input validation shall be performed before business operations are executed.

FastAPI and Pydantic shall be used for request validation.

Example validation concerns include:

- Invalid email format.
- Missing required fields.
- Invalid monitoring interval.
- Invalid URL.
- Invalid rule configuration.
- Invalid notification configuration.

Validation failures shall return an appropriate client error response without executing the affected business operation.

---

## 5.7 Database Errors

Database-related errors shall be handled within the persistence and service layers.

Typical database failures may include:

- Connection failure.
- Constraint violation.
- Transaction failure.
- Unexpected database unavailability.

The application shall:

1. Roll back the active transaction where required.
2. Log the underlying failure.
3. Convert the error into an appropriate application-level exception.
4. Return a safe response to the API client.

Raw database errors should not be exposed to users.

---

## 5.8 External Service Errors

WatchTower interacts with external resources during monitoring and notification delivery.

Examples include:

- Target website unavailable.
- Request timeout.
- Page structure changed.
- Browser automation failure.
- Email delivery failure.
- Push notification failure.

External failures should be isolated from the rest of the application whenever possible.

A failure while monitoring one target should not cause unrelated monitoring tasks to fail.

---

## 5.9 Monitoring Errors

Monitoring failures should be recorded separately from successful monitoring results.

For example:

```text
Monitoring Task
      │
      ▼
Monitoring Engine
      │
      ├── Success ──► Snapshot
      │
      └── Failure ──► Error Logging
```

A failed monitoring execution should not automatically create a History Event because no meaningful business change has necessarily been detected.

Repeated failures may be surfaced to the user through an appropriate application mechanism in future versions.

---

## 5.10 Notification Errors

Notification delivery failures shall not invalidate the underlying History Event.

The intended flow is:

```text
History Event
      │
      ▼
Notification
      │
      ├── Delivered ──► SENT
      │
      └── Failed ────► FAILED
```

A notification failure shall be recorded independently so that the system can support retry or troubleshooting without re-running the monitoring task.

---

## 5.11 Unexpected Errors

Unexpected exceptions should be handled by a centralized exception mechanism.

The centralized handler shall:

- Record the error through the logging system.
- Prevent sensitive details from reaching the client.
- Return a standardized server error response.
- Preserve enough diagnostic information for debugging.

Unexpected errors should not be silently converted into successful responses.

---

## 5.12 Error Logging

Errors should include sufficient contextual information to identify the affected operation.

Where applicable, logs should include:

- Timestamp.
- Log level.
- Component or module.
- Operation being performed.
- Relevant resource identifier.
- Exception information.

Sensitive information such as passwords, authentication tokens, and private credentials shall never be logged.

---

## Chapter Summary

This chapter established the error-handling strategy for WatchTower.

The approach separates internal failures from user-facing responses, uses application-specific exceptions for expected failures, preserves transaction integrity, isolates external service failures, and provides centralized handling for unexpected errors.


# 6. Logging

---

## Chapter Overview

This chapter defines the logging practices used throughout the WatchTower application.

Logging provides visibility into application behavior, monitoring execution, external service interactions, and unexpected failures. The logging strategy should support debugging and operational monitoring without producing unnecessary noise or exposing sensitive information.

---

## 6.1 Logging Principles

The following principles shall guide logging throughout the application:

- Log meaningful application events.
- Use appropriate log levels.
- Avoid excessive or duplicate logging.
- Never log sensitive information.
- Include sufficient context to understand failures.
- Keep logging consistent across application components.
- Use structured and machine-readable logging where practical.

---

## 6.2 Log Levels

WatchTower shall use standard logging levels.

| Level | Purpose |
|-------|---------|
| `DEBUG` | Detailed information useful during development and troubleshooting. |
| `INFO` | Normal application and operational events. |
| `WARNING` | Unexpected conditions that do not immediately prevent operation. |
| `ERROR` | Failures that prevent a specific operation from completing successfully. |
| `CRITICAL` | Severe failures that may affect the availability of the application. |

---

## 6.3 Logging Examples

### DEBUG

Used for detailed information during development.

```python
logger.debug(
    "Evaluating monitoring rule",
    extra={"rule_id": rule_id}
)
```

### INFO

Used for significant normal events.

```python
logger.info(
    "Monitoring task executed",
    extra={"task_id": task_id}
)
```

### WARNING

Used when an unexpected but recoverable condition occurs.

```python
logger.warning(
    "Monitoring target responded slowly",
    extra={"task_id": task_id}
)
```

### ERROR

Used when an operation fails.

```python
logger.error(
    "Notification delivery failed",
    extra={"notification_id": notification_id},
    exc_info=True
)
```

---

## 6.4 Contextual Logging

Logs should contain relevant context whenever possible.

For monitoring operations, useful context may include:

- `task_id`
- `rule_id`
- `snapshot_id`
- `history_event_id`
- `notification_id`

For authenticated operations, a user identifier may be included where appropriate.

Context should help identify the affected operation without exposing private user information unnecessarily.

---

## 6.5 Sensitive Information

The following information shall never be written to application logs:

- Plaintext passwords.
- Password hashes.
- JWT tokens.
- API keys.
- Database credentials.
- Session secrets.
- Private notification content where inappropriate.
- Other sensitive authentication or security information.

Logs should be reviewed before introducing new logging statements that may contain user-provided data.

---

## 6.6 Monitoring Execution Logs

The Monitoring Engine should produce meaningful operational logs.

A typical execution may generate:

```text
Monitoring Task Started
        ↓
Target Accessed
        ↓
Data Extracted
        ↓
Rules Evaluated
        ↓
Snapshot Stored
        ↓
Change Detected
        ↓
History Event Created
```

Only meaningful events should be logged at `INFO` level. Detailed execution information may use `DEBUG` level.

---

## 6.7 Notification Logs

Notification processing should provide enough information to understand delivery outcomes.

Example:

```text
Notification Created
        ↓
Delivery Attempted
        ↓
   ┌────┴────┐
   ↓         ↓
Success     Failure
   ↓         ↓
  INFO      ERROR
```

Notification failures should include the notification identifier and relevant failure context.

Sensitive notification content should not be logged unnecessarily.

---

## 6.8 Development and Production Logging

Logging behavior may differ between development and production environments.

### Development

Development logging may use:

- `DEBUG`
- Detailed error information
- Console output
- More verbose diagnostics

### Production

Production logging should:

- Reduce unnecessary debug output.
- Preserve important operational events.
- Record errors and failures.
- Avoid sensitive information.
- Support centralized log collection when required.

---

## 6.9 Log Format

Where practical, logs should use a structured format suitable for machine processing.

A production log entry may conceptually contain:

```json
{
    "timestamp": "2026-08-11T10:00:00Z",
    "level": "ERROR",
    "component": "notification_service",
    "event": "notification_delivery_failed",
    "notification_id": 42
}
```

The exact logging implementation may evolve as deployment requirements become clearer.

---

## 6.10 Logging and Error Handling

Logging and error handling work together but have different responsibilities.

```text
Exception
    │
    ├── Log diagnostic information
    │
    └── Return safe application/API response
```

An exception should not be logged repeatedly by every layer.

The layer that has sufficient context to handle or report the failure should generally be responsible for the relevant log entry.

---

## 6.11 Logging and Performance

Logging should not become a significant performance bottleneck.

The following practices should be followed:

- Avoid excessive logging inside high-frequency loops.
- Avoid logging large snapshot payloads.
- Avoid unnecessary serialization solely for logging.
- Use appropriate log levels to control verbosity.

Monitoring operations may execute frequently, so logging volume should be considered when designing the Monitoring Engine.

---

## Chapter Summary

This chapter established the logging strategy for WatchTower.

The approach provides useful operational visibility while maintaining performance, avoiding unnecessary noise, and protecting sensitive information. Logging will support both development debugging and future production monitoring.


# 7. Testing Guidelines

---

## Chapter Overview

This chapter defines the testing practices to be followed during WatchTower development.

The testing strategy is intended to verify individual components, interactions between components, and important end-to-end application workflows.

Testing should provide confidence in the system without introducing unnecessary development overhead.

---

## 7.1 Testing Principles

The following principles shall guide testing:

- Test important application behavior rather than implementation details.
- New features should include appropriate tests.
- Critical business logic should have strong test coverage.
- Tests should be deterministic and repeatable.
- Tests should remain independent wherever practical.
- External services should be isolated or mocked during automated tests.
- Tests should be easy to understand and maintain.

---

## 7.2 Testing Levels

WatchTower shall use multiple levels of testing.

| Testing Level | Purpose |
|---------------|---------|
| Unit Testing | Tests individual functions, classes, and isolated components. |
| Integration Testing | Tests interactions between application components and infrastructure. |
| API Testing | Verifies HTTP endpoints, validation, authentication, and responses. |
| End-to-End Testing | Verifies important user workflows across multiple application layers. |

The majority of tests should remain at the unit and integration levels, while end-to-end tests should focus on critical workflows.

---

## 7.3 Unit Testing

Unit tests should verify individual pieces of application logic independently.

Typical targets include:

- Service methods.
- Rule evaluation logic.
- Change detection.
- Validation helpers.
- Utility functions.
- Notification decision logic.

Example:

```python
def test_price_drop_is_detected():
    previous_price = 50000
    current_price = 45000

    result = detect_price_change(
        previous_price,
        current_price
    )

    assert result.is_changed is True
```

Unit tests should avoid unnecessary dependencies on databases, browsers, networks, or external services.

---

## 7.4 Repository Testing

Repository operations should be tested against a controlled test database where appropriate.

Tests should verify operations such as:

- Creating records.
- Retrieving records.
- Updating records.
- Deleting records.
- Foreign key relationships.
- Constraint behavior.

Repository tests should confirm that the persistence layer correctly implements the database design defined in the DDD.

---

## 7.5 API Testing

API tests should verify:

- Request validation.
- Authentication requirements.
- Authorization behavior.
- Successful responses.
- Error responses.
- HTTP status codes.
- Response schemas.

Example workflow:

```text
HTTP Request
     ↓
API Route
     ↓
Service
     ↓
Repository
     ↓
Test Database
     ↓
HTTP Response
```

---

## 7.6 Monitoring Engine Testing

The Monitoring Engine is a critical component and should be tested independently from live websites whenever possible.

Test cases should include:

- Successful target access.
- Target access failure.
- Timeout.
- Data extraction failure.
- Rule evaluation.
- No meaningful change.
- Meaningful change.
- Snapshot creation.
- History event creation.

External websites should not be required for ordinary automated tests.

Controlled fixtures or mocked responses should be preferred.

---

## 7.7 Notification Testing

Notification functionality should be tested independently of real notification providers.

Tests should verify:

- Notification creation.
- Channel selection.
- Delivery success.
- Delivery failure.
- Status updates.
- Error recording.
- Retry behavior where implemented.

External email or push notification services should be mocked during automated tests unless a dedicated integration test environment is being used.

---

## 7.8 Database Testing

Database-related tests should verify the integrity of the schema.

Important areas include:

- Primary key behavior.
- Foreign key relationships.
- Unique constraints.
- Nullable fields.
- Default values.
- Cascade behavior.
- JSONB storage.
- Transaction rollback.

Database tests should use isolated test data and should not modify development or production databases.

---

## 7.9 Authentication Testing

Authentication tests should verify:

- User registration.
- Password hashing.
- Login success.
- Invalid credentials.
- Token generation.
- Protected endpoint access.
- Expired or invalid authentication tokens.
- Unauthorized access attempts.

Authentication-related tests must never use real production credentials or secrets.

---

## 7.10 Test Naming

Test names should clearly describe the behavior being verified.

Preferred:

```python
def test_task_creation_requires_authenticated_user():
    ...


def test_notification_failure_is_recorded():
    ...


def test_stock_change_creates_history_event():
    ...
```

Avoid vague names such as:

```python
def test_task():
    ...


def test_function():
    ...
```

---

## 7.11 Test Organization

Tests should be organized according to their testing level and responsibility.

Recommended structure:

```text
tests/
│
├── unit/
│   ├── test_services.py
│   ├── test_rules.py
│   └── test_utils.py
│
├── integration/
│   ├── test_repositories.py
│   ├── test_database.py
│   └── test_api.py
│
└── e2e/
    └── test_monitoring_workflow.py
```

The structure may evolve as the test suite grows.

---

## 7.12 Test Data

Test data should be:

- Isolated from real user data.
- Reproducible.
- Minimal where possible.
- Representative of realistic scenarios.

Sensitive or production data shall not be copied directly into the test environment.

---

## 7.13 External Services

External services should generally be mocked or controlled during automated tests.

Examples include:

- External websites.
- Email providers.
- Browser automation targets.
- Push notification services.
- Third-party APIs.

Dedicated integration tests may use real services when required, but such tests should be clearly separated from the normal automated test suite.

---

## 7.14 Test Execution

Tests should be executed regularly during development.

Before merging significant changes, the relevant automated test suite should pass.

A typical development workflow is:

```text
Implement Change
      ↓
Run Relevant Tests
      ↓
Fix Failures
      ↓
Run Full Test Suite
      ↓
Review
      ↓
Commit
```

---

## 7.15 Coverage

Code coverage may be used as a supporting quality metric.

Coverage should not be treated as the sole measure of test quality.

Priority should be given to testing:

- Authentication.
- Monitoring logic.
- Rule evaluation.
- Change detection.
- Database integrity.
- Notification processing.
- Important API workflows.

---

## Chapter Summary

This chapter established a practical testing strategy for WatchTower.

The approach combines unit, integration, API, database, and end-to-end testing while prioritizing critical business logic and keeping external dependencies isolated from ordinary automated tests.


# 8. Git & Version Control

---

## Chapter Overview

This chapter defines the Git and version control practices to be followed during WatchTower development.

Version control shall be used to maintain a clear development history, isolate changes, and provide a reliable mechanism for reviewing and recovering previous versions of the project.

---

## 8.1 Repository

The WatchTower source code shall be maintained in a Git repository.

The repository should contain:

- Application source code.
- Automated tests.
- Database migration files.
- Documentation.
- Configuration templates.
- Dependency definitions.

Generated files, local environments, secrets, and temporary development files shall not be committed.

---

## 8.2 Branching Strategy

The project shall use a simple branching strategy appropriate for a small development team.

```text
main
 │
 ├── feature/authentication
 ├── feature/monitoring
 ├── feature/notifications
 └── fix/notification-error
```

### Main Branch

The `main` branch shall contain stable and reviewable code.

Direct development on `main` should generally be avoided.

### Feature Branches

New functionality should be developed in dedicated feature branches.

Example:

```text
feature/monitoring-task
feature/price-monitoring
feature/browser-notifications
```

### Fix Branches

Bug fixes should use a dedicated fix branch.

Example:

```text
fix/task-scheduler
fix/login-validation
```

---

## 8.3 Commit Guidelines

Commits should represent a meaningful logical change.

A commit should avoid combining unrelated modifications.

### Preferred

```text
Add monitoring task creation API
```

```text
Implement price change detection
```

```text
Fix notification retry handling
```

### Avoid

```text
changes
```

```text
final
```

```text
updated everything
```

---

## 8.4 Commit Message Format

Where practical, commit messages should follow a simple action-oriented format.

```text
<action> <change>
```

Examples:

```text
Add user authentication
Implement monitoring scheduler
Update notification service
Fix task ownership validation
Refactor monitoring repository
```

The project does not require an overly strict commit-message framework.

Clarity is more important than ceremony.

---

## 8.5 Pull Requests

When multiple developers are contributing, feature branches should be reviewed before merging into `main`.

A pull request should generally contain:

- A clear description of the change.
- Relevant implementation details.
- Tests performed.
- Any important migration or configuration changes.

For solo development, the same review process may be performed as a self-review before merging.

---

## 8.6 Database Migrations

Database schema changes shall be committed together with their corresponding migration files.

For example:

```text
Code Change
     +
Alembic Migration
     +
Tests
```

A schema change should not rely on manually modifying the development database.

The DDD remains the reference for the intended database structure.

---

## 8.7 Documentation Changes

Documentation changes should be committed alongside the implementation when they describe or affect that implementation.

Examples include:

- API changes.
- Database changes.
- Architectural changes.
- New development procedures.

Significant architectural decisions should also be recorded in the appropriate project documentation.

---

## 8.8 Commit Scope

Commits should remain reasonably focused.

For example, the following changes should preferably be separated:

```text
Add monitoring task model
Add monitoring task repository
Add monitoring task API
Add monitoring task tests
```

However, closely related implementation changes may be combined into a single commit when separating them would make the history less meaningful.

---

## 8.9 Version Tags

Stable milestones may be tagged in Git.

Example:

```text
v0.1.0
v0.2.0
v1.0.0
```

Versioning should become more formal as WatchTower approaches a production release.

---

## 8.10 Sensitive Files

The following shall never be committed to the repository:

```text
.env
```

Private keys, API credentials, database passwords, authentication secrets, and other sensitive configuration values shall also be excluded.

A safe configuration template should be provided instead:

```text
.env.example
```

Example:

```env
DATABASE_URL=
SECRET_KEY=
EMAIL_HOST=
EMAIL_USERNAME=
EMAIL_PASSWORD=
```

Actual values shall remain in the local environment or approved secret-management system.

---

## 8.11 `.gitignore`

The repository shall include an appropriate `.gitignore` file.

It should exclude common local and generated files such as:

```text
__pycache__/
*.pyc
.venv/
.env
.pytest_cache/
.coverage
```

Additional generated files shall be added as the project evolves.

---

## Chapter Summary

This chapter established a lightweight Git workflow for WatchTower.

The approach emphasizes meaningful commits, isolated feature development, safe configuration management, and a clean project history without introducing unnecessary version-control complexity.


# 9. Environment & Configuration

---

## Chapter Overview

This chapter defines how WatchTower manages application configuration across development, testing, and production environments.

Configuration should remain separate from application source code so that environment-specific values can be changed without modifying the codebase.

Sensitive configuration values shall be stored securely and shall never be committed to the Git repository.

---

## 9.1 Configuration Principles

The following principles shall be followed:

- Environment-specific configuration should not be hardcoded.
- Sensitive values shall be provided through environment variables or an approved secret-management mechanism.
- Default values may be provided for safe non-sensitive configuration where appropriate.
- Configuration should be loaded centrally.
- Development, testing, and production environments should remain independently configurable.
- Configuration changes should not require modification of application logic.

---

## 9.2 Environment Variables

WatchTower shall use environment variables for configuration values that may differ between environments.

Examples include:

```env
DATABASE_URL=
SECRET_KEY=
DEBUG=
ENVIRONMENT=
```

Additional variables may be introduced as new infrastructure or integrations are added.

---

## 9.3 Environment File

During local development, environment variables may be stored in a local `.env` file.

Example:

```env
DATABASE_URL=postgresql://user:password@localhost/watchtower
SECRET_KEY=development-secret
DEBUG=true
ENVIRONMENT=development
```

The `.env` file shall not be committed to the repository.

A `.env.example` file shall be maintained to document the required configuration keys without containing real credentials.

---

## 9.4 Configuration Management

Application configuration shall be loaded through a centralized configuration component.

Example:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    environment: str = "development"


settings = Settings()
```

Application components should access configuration through the centralized settings object rather than reading environment variables directly throughout the codebase.

---

## 9.5 Environment Separation

WatchTower shall support separate configuration for different environments.

| Environment | Purpose |
|-------------|---------|
| Development | Local feature development and debugging. |
| Testing | Automated and isolated testing. |
| Production | Deployed application environment. |

Each environment may use different:

- Database connections.
- Security keys.
- Logging levels.
- External service credentials.
- Debug settings.
- Notification providers.

---

## 9.6 Development Configuration

Development configuration should prioritize ease of development and debugging.

Typical characteristics include:

```text
DEBUG=true
ENVIRONMENT=development
```

Development environments may use local services or dedicated development resources.

Production credentials and production databases shall not be used for ordinary local development.

---

## 9.7 Testing Configuration

Testing should use an isolated environment.

Test configuration may include:

```text
ENVIRONMENT=testing
```

The test environment should use:

- A dedicated test database.
- Test-specific credentials.
- Mock or controlled external services.
- Test-safe configuration values.

Tests must not modify production data.

---

## 9.8 Production Configuration

Production configuration shall prioritize security and reliability.

Typical requirements include:

- Debug mode disabled.
- Strong secret keys.
- Secure database credentials.
- Production notification credentials.
- Appropriate logging configuration.
- Secure external service configuration.

Production secrets should be provided through environment variables or a dedicated secret-management system.

---

## 9.9 Secret Management

Sensitive values shall never be stored directly in source code.

Sensitive information includes:

- Database passwords.
- Application secret keys.
- API keys.
- Email credentials.
- Authentication secrets.
- Third-party service credentials.

Example:

```python
# Avoid
SECRET_KEY = "my-secret-key"
```

Instead, configuration should be supplied through the environment:

```env
SECRET_KEY=<secure-value>
```

---

## 9.10 Configuration Validation

Required configuration values should be validated when the application starts.

If a required configuration value is missing or invalid, the application should fail clearly during startup rather than operating with an incomplete configuration.

Example:

```text
Application Startup
        ↓
Load Configuration
        ↓
Validate Configuration
        │
   ┌────┴────┐
   ↓         ↓
 Valid     Invalid
   ↓         ↓
 Start     Fail Fast
```

This prevents configuration problems from appearing later during application execution.

---

## 9.11 Configuration Changes

Configuration changes should be treated separately from code changes where possible.

Changes to environment-specific values should not require modifications to application source code.

When a new required configuration variable is introduced:

1. Add it to the centralized configuration model.
2. Add the variable to `.env.example`.
3. Document its purpose where necessary.
4. Update deployment configuration.
5. Verify application startup and relevant tests.

---

## 9.12 Local Development Dependencies

Local development should use an isolated Python environment.

Example:

```text
.venv/
```

The virtual environment should not be committed to Git.

Dependencies shall be defined in the project's dependency management file and installed consistently across environments.

---

## Chapter Summary

This chapter established the environment and configuration practices for WatchTower.

Configuration is separated from application code, sensitive values are protected, environments remain isolated, and centralized configuration validation ensures that the application starts only when its required configuration is valid.


# 10. Development Workflow

---

## Chapter Overview

This chapter defines the general workflow to be followed during WatchTower development.

The workflow is intended to keep implementation organized while remaining lightweight enough for a small development team. It provides a consistent sequence for planning, implementing, testing, reviewing, and integrating changes.

---

## 10.1 Development Cycle

A typical development cycle shall follow:

```text
Requirement
    ↓
Design / Review
    ↓
Implementation
    ↓
Testing
    ↓
Self-Review
    ↓
Commit
    ↓
Integration
```

The exact process may be shortened for small changes where a full cycle is unnecessary.

---

## 10.2 Feature Development

New features should generally follow these steps:

### 1. Understand the Requirement

Review the relevant requirements and determine the expected behavior.

Relevant documentation may include:

- SRS
- SAD
- DDD
- API Design Document
- Existing implementation

### 2. Review the Design

Determine whether the feature fits within the existing architecture.

If the feature requires a significant architectural or database change, the relevant documentation should be updated before implementation.

### 3. Implement

Develop the feature within the appropriate architectural layer.

For example:

```text
API
 ↓
Service
 ↓
Repository
 ↓
Database
```

Monitoring, scheduling, and notification functionality should follow their corresponding architectural boundaries.

### 4. Test

Run the relevant unit and integration tests.

New functionality should include appropriate tests where practical.

### 5. Review

Review the implementation for:

- Correctness.
- Readability.
- Architectural consistency.
- Error handling.
- Security concerns.
- Unnecessary duplication.
- Test coverage.

### 6. Commit

Create a meaningful Git commit containing the completed logical change.

---

## 10.3 Database Changes

Database changes shall follow a controlled process.

```text
Identify Schema Change
        ↓
Update DDD
        ↓
Update SQLAlchemy Model
        ↓
Create Alembic Migration
        ↓
Run Migration
        ↓
Run Tests
        ↓
Commit Changes
```

The database shall not be modified manually as a substitute for migration files.

When a schema change affects application behavior, the relevant services, repositories, API schemas, and tests shall also be updated.

---

## 10.4 API Changes

Changes to API behavior should be reflected in the API Design Document.

The following should be considered when modifying an endpoint:

- Request structure.
- Response structure.
- Authentication requirements.
- Authorization behavior.
- HTTP status codes.
- Validation.
- Error responses.
- Related tests.

API implementation should remain consistent with the documented contract.

---

## 10.5 Architectural Changes

Not every code change requires architectural documentation.

However, documentation should be reviewed when a change:

- Introduces a new major component.
- Changes communication between architectural layers.
- Changes database ownership or relationships.
- Introduces a new external service.
- Changes a significant security mechanism.
- Alters an established architectural decision.

Significant architectural decisions should be documented before or alongside implementation.

---

## 10.6 Dependency Management

New dependencies should be introduced only when they provide meaningful value.

Before adding a dependency, consider:

- Whether the functionality can reasonably be implemented using existing dependencies.
- Whether the dependency is actively maintained.
- Whether it introduces unnecessary complexity.
- Whether it is compatible with the project architecture.
- Whether its licensing is appropriate.

Dependencies shall be recorded in the project's dependency configuration.

---

## 10.7 Code Review

Code should be reviewed before being considered complete.

The review should verify:

### Functionality

- Does the implementation satisfy the requirement?
- Are important edge cases handled?

### Architecture

- Does the implementation follow the established architecture?
- Is business logic in the correct layer?

### Database

- Are schema changes consistent with the DDD?
- Are migrations included where required?

### Security

- Are credentials and sensitive data protected?
- Is user authorization enforced?

### Quality

- Is the code readable?
- Is unnecessary duplication avoided?
- Are appropriate tests included?

---

## 10.8 Definition of Done

A feature may be considered complete when:

- The required functionality has been implemented.
- Relevant tests pass.
- Error handling has been considered.
- Security implications have been reviewed.
- Required database migrations are included.
- Relevant documentation has been updated.
- The code follows the established project structure and conventions.
- The change has been committed to Git.

Not every small change requires updates to every document. Documentation should be updated only where the change materially affects the documented design or behavior.

---

## 10.9 Development Priorities

When making implementation decisions, the following priorities should generally apply:

```text
Correctness
    ↓
Security
    ↓
Maintainability
    ↓
Simplicity
    ↓
Performance Optimization
```

Performance should not be optimized prematurely at the cost of correctness or maintainability.

Where performance becomes a demonstrated problem, optimization should be guided by measurement rather than assumption.

---

## 10.10 Handling Uncertainty

If implementation reveals that an existing design decision is insufficient, the team should not force the implementation to fit a flawed design.

Instead:

```text
Identify Problem
      ↓
Evaluate Alternatives
      ↓
Review Impact
      ↓
Update Relevant Documentation
      ↓
Implement Revised Design
```

This ensures that the documentation remains an accurate representation of the actual system rather than becoming outdated while development continues.

---

## 10.11 Development Workflow Summary

The overall WatchTower development workflow can be summarized as:

```text
Requirement
    │
    ▼
Review Existing Design
    │
    ▼
Determine Required Changes
    │
    ▼
Update Documentation if Necessary
    │
    ▼
Implement
    │
    ▼
Test
    │
    ▼
Review
    │
    ▼
Commit
    │
    ▼
Integrate
```

---

## Chapter Summary

This chapter established the development workflow for WatchTower.

The workflow provides a lightweight but disciplined process for implementing features, handling database and API changes, reviewing code, maintaining documentation, and integrating completed work.

The process is intentionally flexible so that small changes do not become unnecessarily bureaucratic while significant changes receive the level of review they require.

---

# Development Guidelines Conclusion

The Development Guidelines establish the practical standards that will govern WatchTower implementation.

Together, these guidelines provide a consistent foundation for:

- Project organization.
- Coding practices.
- Naming.
- Error handling.
- Logging.
- Testing.
- Version control.
- Configuration management.
- Feature development.

These guidelines complement the **Software Requirements Specification (SRS)**, **Software Architecture Design (SAD)**, and **Database Design Document (DDD)**.

The next development document will define the API contracts through which the WatchTower frontend, backend services, and other components communicate.

**End of Development Guidelines**