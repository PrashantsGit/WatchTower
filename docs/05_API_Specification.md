# WatchTower

# API Design Document

---

**Document Version:** 1.0

**Document Status:** Draft

**Prepared By:** Team WatchTower

**Related Documents:**

- Software Requirements Specification (SRS)
- Software Architecture Design (SAD)
- Database Design Document (DDD)
- Development Guidelines

---

# 1. Introduction

## Chapter Overview

This document defines the HTTP API exposed by the WatchTower backend.

The API provides the communication interface between the WatchTower frontend and backend services and is responsible for authentication, monitoring task management, rules, monitoring history, notifications, and user settings.

The API follows REST principles and uses JSON for request and response payloads.

---

## 1.1 Purpose

The purpose of this document is to define:

- API endpoints.
- HTTP methods.
- Request structures.
- Response structures.
- Authentication requirements.
- Validation expectations.
- HTTP status codes.
- Error response conventions.

---

## 1.2 Scope

The API covers the following functional areas:

- Authentication
- User account management
- Monitoring tasks
- Monitoring rules
- Monitoring history
- Notifications
- User settings

Monitoring execution itself is handled internally by the Monitoring Engine and Scheduler rather than being directly controlled by public API endpoints.

---

## 1.3 API Principles

The WatchTower API follows these principles:

- REST-oriented resource design.
- JSON request and response bodies.
- JWT-based authentication.
- Clear HTTP status codes.
- Consistent error responses.
- Stateless API requests.
- API routes remain thin and delegate business logic to services.

---

# 2. API Architecture

---

## 2.1 Request Flow

API requests follow the architecture defined in the SAD.

```text
Client
  │
  ▼
API Route
  │
  ▼
Authentication / Validation
  │
  ▼
Service Layer
  │
  ▼
Repository Layer
  │
  ▼
Database
```

The API layer shall not directly contain database operations or complex business logic.

---

## 2.2 Base URL

The API shall use the following base structure:

```text
/api
```

Resource endpoints are defined relative to this base path.

Examples:

```text
/api/auth/login
/api/tasks
/api/notifications
```

The final deployment URL may vary by environment.

---

## 2.3 Content Type

JSON shall be used for API request and response bodies unless an endpoint explicitly requires another format.

Requests containing JSON shall use:

```http
Content-Type: application/json
```

Successful JSON responses shall generally use:

```http
Content-Type: application/json
```

---

## 2.4 Authentication

Protected endpoints require a valid JWT access token.

The token shall be supplied using the HTTP Authorization header:

```http
Authorization: Bearer <access_token>
```

Unauthenticated endpoints such as registration and login do not require a JWT.

---

# 3. Authentication API

---

## 3.1 Register User

### Endpoint

```http
POST /api/auth/register
```

### Authentication

Not required.

### Request

```json
{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "secure-password"
}
```

### Response

```json
{
    "message": "User registered successfully.",
    "user": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com"
    }
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `201 Created` | User successfully registered. |
| `400 Bad Request` | Invalid registration request. |
| `409 Conflict` | Email already exists. |
| `422 Unprocessable Entity` | Request validation failed. |

Passwords shall never be returned in API responses.

---

## 3.2 Login

### Endpoint

```http
POST /api/auth/login
```

### Authentication

Not required.

### Request

```json
{
    "email": "john@example.com",
    "password": "secure-password"
}
```

### Response

```json
{
    "access_token": "<jwt-token>",
    "token_type": "bearer"
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Authentication successful. |
| `401 Unauthorized` | Invalid credentials. |
| `422 Unprocessable Entity` | Request validation failed. |

---

## 3.3 Get Current User

### Endpoint

```http
GET /api/auth/me
```

### Authentication

Required.

### Response

```json
{
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "is_verified": true,
    "is_active": true
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | User information retrieved. |
| `401 Unauthorized` | Invalid or missing token. |

---

# 4. Monitoring Task API

---

## 4.1 List Monitoring Tasks

### Endpoint

```http
GET /api/tasks
```

### Authentication

Required.

### Response

```json
{
    "items": [
        {
            "id": 1,
            "name": "Pixel 8a Price",
            "description": "Monitor Pixel 8a price",
            "target_url": "https://example.com/product",
            "check_interval": 60,
            "is_active": true,
            "last_checked_at": null,
            "next_execution_at": null,
            "created_at": "2026-08-11T10:00:00Z"
        }
    ]
}
```

The API shall return only tasks belonging to the authenticated user.

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Tasks retrieved successfully. |
| `401 Unauthorized` | Authentication required. |

---

## 4.2 Create Monitoring Task

### Endpoint

```http
POST /api/tasks
```

### Authentication

Required.

### Request

```json
{
    "name": "Pixel 8a Price",
    "description": "Monitor Pixel 8a price",
    "target_url": "https://example.com/product",
    "check_interval": 60
}
```

### Response

```json
{
    "id": 1,
    "name": "Pixel 8a Price",
    "description": "Monitor Pixel 8a price",
    "target_url": "https://example.com/product",
    "check_interval": 60,
    "is_active": true
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `201 Created` | Task created successfully. |
| `400 Bad Request` | Invalid task data. |
| `401 Unauthorized` | Authentication required. |
| `422 Unprocessable Entity` | Validation failed. |

---

## 4.3 Get Monitoring Task

### Endpoint

```http
GET /api/tasks/{task_id}
```

### Authentication

Required.

### Response

```json
{
    "id": 1,
    "name": "Pixel 8a Price",
    "description": "Monitor Pixel 8a price",
    "target_url": "https://example.com/product",
    "check_interval": 60,
    "is_active": true,
    "last_checked_at": null,
    "next_execution_at": null
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Task retrieved successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Task does not exist or does not belong to the user. |

---

## 4.4 Update Monitoring Task

### Endpoint

```http
PUT /api/tasks/{task_id}
```

### Authentication

Required.

### Request

```json
{
    "name": "Pixel 8a Price Updated",
    "description": "Updated monitoring description",
    "target_url": "https://example.com/product",
    "check_interval": 120
}
```

### Response

Returns the updated monitoring task.

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Task updated successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Task does not exist or does not belong to the user. |
| `422 Unprocessable Entity` | Validation failed. |

---

## 4.5 Delete Monitoring Task

### Endpoint

```http
DELETE /api/tasks/{task_id}
```

### Authentication

Required.

### Response

```json
{
    "message": "Monitoring task deleted successfully."
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Task deleted successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Task does not exist or does not belong to the user. |

Associated child records are handled according to the cascade rules defined in the DDD.

---

## 4.6 Pause Monitoring Task

### Endpoint

```http
POST /api/tasks/{task_id}/pause
```

### Authentication

Required.

### Response

```json
{
    "message": "Monitoring task paused.",
    "is_active": false
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Task paused successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Task does not exist or does not belong to the user. |

---

## 4.7 Resume Monitoring Task

### Endpoint

```http
POST /api/tasks/{task_id}/resume
```

### Authentication

Required.

### Response

```json
{
    "message": "Monitoring task resumed.",
    "is_active": true
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Task resumed successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Task does not exist or does not belong to the user. |

---

# 5. Monitoring Rule API

---

## 5.1 List Rules

### Endpoint

```http
GET /api/tasks/{task_id}/rules
```

### Authentication

Required.

### Response

```json
{
    "items": [
        {
            "id": 1,
            "rule_type": "PRICE",
            "operator": "<",
            "target_value": "50000",
            "is_enabled": true
        }
    ]
}
```

Only rules belonging to the authenticated user's task may be returned.

---

## 5.2 Create Rule

### Endpoint

```http
POST /api/tasks/{task_id}/rules
```

### Authentication

Required.

### Request

```json
{
    "rule_type": "PRICE",
    "operator": "<",
    "target_value": "50000"
}
```

### Response

```json
{
    "id": 1,
    "task_id": 1,
    "rule_type": "PRICE",
    "operator": "<",
    "target_value": "50000",
    "is_enabled": true
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `201 Created` | Rule created successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Monitoring task does not exist or is not owned by the user. |
| `422 Unprocessable Entity` | Invalid rule data. |

The application layer is responsible for validating supported rule types and operators.

The API does not hardcode application-specific monitoring strategies into the database schema.

---

## 5.3 Update Rule

### Endpoint

```http
PUT /api/tasks/{task_id}/rules/{rule_id}
```

### Authentication

Required.

### Request

```json
{
    "rule_type": "PRICE",
    "operator": "<",
    "target_value": "45000",
    "is_enabled": true
}
```

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Rule updated successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Task or rule does not exist or is not accessible. |
| `422 Unprocessable Entity` | Invalid rule data. |

---

## 5.4 Delete Rule

### Endpoint

```http
DELETE /api/tasks/{task_id}/rules/{rule_id}
```

### Authentication

Required.

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Rule deleted successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Rule does not exist or is not accessible. |

---

# 6. History API

---

## 6.1 List History Events

### Endpoint

```http
GET /api/history
```

### Authentication

Required.

### Response

```json
{
    "items": [
        {
            "id": 42,
            "task_id": 1,
            "rule_id": 1,
            "event_type": "PRICE_DROP",
            "previous_value": "52999",
            "current_value": "49999",
            "event_message": "Price dropped from 52999 to 49999.",
            "detected_at": "2026-08-11T09:30:00Z"
        }
    ]
}
```

Only history events belonging to the authenticated user shall be returned.

---

## 6.2 Get Task History

### Endpoint

```http
GET /api/tasks/{task_id}/history
```

### Authentication

Required.

### Response

Returns history events associated with the specified monitoring task.

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | History retrieved successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Task does not exist or is not accessible. |

---

# 7. Notification API

---

## 7.1 List Notifications

### Endpoint

```http
GET /api/notifications
```

### Authentication

Required.

### Response

```json
{
    "items": [
        {
            "id": 10,
            "history_event_id": 42,
            "notification_channel": "EMAIL",
            "notification_status": "SENT",
            "delivered_at": "2026-08-11T09:31:00Z",
            "created_at": "2026-08-11T09:30:30Z"
        }
    ]
}
```

Only notifications associated with the authenticated user shall be returned.

---

## 7.2 Get Notification

### Endpoint

```http
GET /api/notifications/{notification_id}
```

### Authentication

Required.

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Notification retrieved successfully. |
| `401 Unauthorized` | Authentication required. |
| `404 Not Found` | Notification does not exist or is not accessible. |

---

## 7.3 Notification Preferences

### Get Preferences

```http
GET /api/notifications/preferences
```

### Authentication

Required.

### Response

```json
{
    "email_enabled": true,
    "browser_push_enabled": true,
    "notify_on_price_change": true,
    "notify_on_stock_change": true
}
```

### Update Preferences

```http
PUT /api/notifications/preferences
```

### Request

```json
{
    "email_enabled": true,
    "browser_push_enabled": false,
    "notify_on_price_change": true,
    "notify_on_stock_change": true
}
```

The endpoint updates the authenticated user's notification preferences.

---

# 8. User API

---

## 8.1 Get User Profile

### Endpoint

```http
GET /api/users/me
```

### Authentication

Required.

### Response

```json
{
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com"
}
```

---

## 8.2 Update User Profile

### Endpoint

```http
PUT /api/users/me
```

### Authentication

Required.

### Request

```json
{
    "full_name": "John Smith"
}
```

### Response

Returns the updated user profile.

---

# 9. Dashboard API

---

## 9.1 Dashboard Summary

### Endpoint

```http
GET /api/dashboard
```

### Authentication

Required.

### Response

```json
{
    "total_tasks": 10,
    "active_tasks": 7,
    "paused_tasks": 3,
    "recent_events": 5,
    "pending_notifications": 2
}
```

The dashboard endpoint provides aggregated information required by the frontend dashboard.

The exact metrics may evolve as dashboard requirements become clearer.

---

# 10. Common API Behavior

---

## 10.1 Authentication Header

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

Invalid or expired tokens shall result in:

```http
401 Unauthorized
```

---

## 10.2 Resource Ownership

Authenticated users may access only resources belonging to them.

For example:

```text
User A
  │
  ├── Task 1
  └── Task 2

User B
  │
  └── Task 3
```

User A must not be able to access Task 3 by changing the task identifier in an API request.

Ownership validation shall therefore be performed at the service or repository level rather than relying solely on the frontend.

---

## 10.3 Validation

Request validation shall be performed using Pydantic schemas.

Invalid requests should be rejected before business operations are executed.

---

## 10.4 Pagination

Collection endpoints may support pagination as the amount of stored data increases.

Potential query parameters include:

```text
?page=1&limit=20
```

Pagination should be introduced where collection size makes it necessary rather than adding complexity to every endpoint from the beginning.

---

# 11. Standard Error Responses

---

## 11.1 Error Structure

API errors should follow a consistent structure:

```json
{
    "error": {
        "code": "TASK_NOT_FOUND",
        "message": "The requested monitoring task was not found."
    }
}
```

---

## 11.2 Common Error Codes

| Code | Meaning |
|------|---------|
| `VALIDATION_ERROR` | Request validation failed. |
| `AUTHENTICATION_REQUIRED` | Authentication is required. |
| `INVALID_CREDENTIALS` | Login credentials are invalid. |
| `FORBIDDEN` | User is not authorized to perform the operation. |
| `RESOURCE_NOT_FOUND` | Requested resource does not exist. |
| `CONFLICT` | Operation conflicts with current state. |
| `INTERNAL_ERROR` | Unexpected server error. |
| `EXTERNAL_SERVICE_ERROR` | External service operation failed. |

Specific resources may introduce more detailed application error codes where useful.

---

# 12. HTTP Status Code Guidelines

| Status | Usage |
|--------|-------|
| `200 OK` | Successful retrieval or update. |
| `201 Created` | Successful resource creation. |
| `204 No Content` | Successful operation with no response body where appropriate. |
| `400 Bad Request` | Invalid request. |
| `401 Unauthorized` | Authentication missing or invalid. |
| `403 Forbidden` | Authenticated user lacks permission. |
| `404 Not Found` | Resource does not exist or is inaccessible. |
| `409 Conflict` | Resource state conflicts with the requested operation. |
| `422 Unprocessable Entity` | Request validation failure. |
| `500 Internal Server Error` | Unexpected server failure. |
| `503 Service Unavailable` | Required service temporarily unavailable. |

---

# 13. API Security

---

## 13.1 Authentication

Protected resources shall require JWT authentication.

---

## 13.2 Authorization

Authentication alone does not grant access to another user's resources.

Every protected resource operation shall verify ownership or appropriate authorization.

---

## 13.3 Input Validation

All client-provided input shall be validated before being processed.

---

## 13.4 Sensitive Data

API responses shall never expose:

- Passwords.
- Password hashes.
- JWT signing secrets.
- Database credentials.
- Internal service credentials.
- Other sensitive configuration values.

---

## 13.5 HTTPS

Production API communication shall use HTTPS.

Authentication tokens and other sensitive data shall not be transmitted over unencrypted connections.

---

# 14. Endpoint Summary

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|:----:|
| POST | `/api/auth/register` | Register user | No |
| POST | `/api/auth/login` | Authenticate user | No |
| GET | `/api/auth/me` | Get authenticated user | Yes |
| GET | `/api/users/me` | Get profile | Yes |
| PUT | `/api/users/me` | Update profile | Yes |
| GET | `/api/tasks` | List tasks | Yes |
| POST | `/api/tasks` | Create task | Yes |
| GET | `/api/tasks/{task_id}` | Get task | Yes |
| PUT | `/api/tasks/{task_id}` | Update task | Yes |
| DELETE | `/api/tasks/{task_id}` | Delete task | Yes |
| POST | `/api/tasks/{task_id}/pause` | Pause task | Yes |
| POST | `/api/tasks/{task_id}/resume` | Resume task | Yes |
| GET | `/api/tasks/{task_id}/rules` | List rules | Yes |
| POST | `/api/tasks/{task_id}/rules` | Create rule | Yes |
| PUT | `/api/tasks/{task_id}/rules/{rule_id}` | Update rule | Yes |
| DELETE | `/api/tasks/{task_id}/rules/{rule_id}` | Delete rule | Yes |
| GET | `/api/history` | List history | Yes |
| GET | `/api/tasks/{task_id}/history` | Get task history | Yes |
| GET | `/api/notifications` | List notifications | Yes |
| GET | `/api/notifications/{notification_id}` | Get notification | Yes |
| GET | `/api/notifications/preferences` | Get preferences | Yes |
| PUT | `/api/notifications/preferences` | Update preferences | Yes |
| GET | `/api/dashboard` | Get dashboard summary | Yes |

---

# 15. API Evolution

The API shall evolve without unnecessarily breaking existing clients.

When introducing new functionality:

- Existing endpoints should remain compatible where practical.
- New resources should use new endpoints rather than overloading unrelated endpoints.
- Breaking changes should be explicitly documented.
- API versioning may be introduced when the application reaches a stage where breaking changes become necessary.

The initial API does not require multiple API versions.

---

# 16. Implementation Notes

The API specification defines the external contract, while implementation details remain within the backend architecture.

The following responsibilities remain separated:

```text
API
 │
 ├── Request / Response
 ├── Authentication
 └── Validation
       │
       ▼
Service
 │
 └── Business Logic
       │
       ▼
Repository
 │
 └── Persistence
       │
       ▼
Database
```

The API shall not directly depend on database implementation details.

---

## Chapter Summary

This document defines the initial REST API contract for WatchTower Version 1.0.

It establishes authentication, monitoring task management, monitoring rules, history, notifications, user settings, dashboard access, validation, error handling, security, and resource ownership.

The API is intentionally designed to remain simple during the initial implementation while providing sufficient structure for future expansion.

---

# Document Conclusion

The API Design Document completes the primary implementation documentation for WatchTower Version 1.0.

Together, the project's documentation now defines:

| Document | Defines |
|----------|--------|
| SRS | What the system must do |
| SAD | How the system is architected |
| DDD | How the data is structured |
| Development Guidelines | How the system is developed |
| API Design Document | How the system communicates |

These documents form the implementation blueprint for the first development phase of WatchTower.

**End of Document**