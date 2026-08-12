<!-- ========================================================= -->
<!--                     SOFTWARE REQUIREMENTS                  -->
<!-- ========================================================= -->

# WatchTower

## Configurable Web Monitoring and Change Detection Platform

### Software Requirements Specification (SRS)

---

**Document Version:** 1.1 (Draft)

**Document Status:** Draft

**Prepared By:** Team WatchTower

**Date:** July 2026

---

> **Document Purpose**
>
> This Software Requirements Specification (SRS) defines the functional and non-functional requirements for WatchTower Version 1.0. It serves as the primary reference for project planning, software design, implementation, testing, deployment, and future maintenance.

---

## Document Information

| Field | Value |
|--------|-------|
| Project Name | WatchTower |
| Document | Software Requirements Specification |
| Version | 1.1 (Draft) |
| Language | English |
| Prepared By | Team WatchTower |
| Intended Audience | Developers, Reviewers, Testers, Project Supervisors |
| Approval Status | Draft |

---

## Revision History

| Version | Date | Description | Author |
|:--------:|------|-------------|--------|
| 1.0 | July 2026 | Initial Draft | Team WatchTower |
| **1.1** | July 2026 | Editorial improvements, formatting, traceability preparation, structural refinement | Team WatchTower |

---

## Document Conventions

The following keywords are used throughout this document.

| Keyword | Meaning |
|----------|---------|
| **Shall** | Mandatory system requirement |
| **Should** | Recommended implementation |
| **May** | Optional capability or future enhancement |

Requirement identifiers follow the conventions below.

| Prefix | Description |
|---------|-------------|
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| BR | Business Rule |
| UI | User Interface Requirement |
| API | API Requirement |
| AD | Architectural Decision |

---

# Table of Contents

1. Introduction

2. Overall Description

3. Functional Requirements

4. External Interface Requirements

5. Non-Functional Requirements

6. Future Scope

7. Appendices

Appendix A — Glossary

Appendix B — Technology Stack

Appendix C — Supporting Documents

Appendix D — Architectural Decisions

Appendix E — Requirement Traceability Matrix

# 1. Introduction

---

## Chapter Overview

This chapter introduces WatchTower and defines the purpose, objectives, scope, terminology, references, and conventions used throughout this Software Requirements Specification (SRS).

It establishes the foundation for understanding the system requirements presented in subsequent chapters and provides a common reference for developers, reviewers, testers, project supervisors, and future contributors.

---

## 1.1 Purpose

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for **WatchTower**, a configurable web monitoring and change detection platform.

The primary purpose of this document is to establish a shared understanding of the system's expected functionality, quality attributes, constraints, and overall scope before implementation begins. It serves as the authoritative reference for software design, development, testing, deployment, and maintenance throughout the project lifecycle.

This specification describes the requirements for **WatchTower Version 1.0** and provides the baseline against which the application will be designed, implemented, verified, and evaluated.

---

## 1.2 Product Overview

WatchTower is a configurable web monitoring platform that enables users to monitor publicly accessible web resources and receive notifications whenever predefined monitoring conditions are satisfied.

Unlike traditional monitoring applications that focus on a single use case, WatchTower adopts a rule-driven architecture in which users create monitoring tasks and define one or more monitoring rules for each task. This approach enables the platform to support multiple monitoring scenarios without requiring modifications to the underlying application.

Examples of supported monitoring scenarios include:

- Product price monitoring
- Stock availability monitoring
- Keyword monitoring
- Rating monitoring
- HTML element monitoring
- General webpage content monitoring

Whenever a monitoring rule detects a meaningful change, WatchTower records the event, preserves monitoring history, and notifies the user through one or more configured notification channels.

Version 1.0 focuses on delivering a reliable, modular, and extensible monitoring platform. Advanced capabilities such as AI-assisted change analysis, collaborative workspaces, browser extensions, and additional notification providers are intentionally deferred to future releases.

---

## 1.3 Objectives

The objectives of WatchTower Version 1.0 are to:

- Provide secure user authentication and account management.
- Allow users to create, configure, and manage monitoring tasks.
- Support multiple configurable monitoring rules for each monitoring task.
- Periodically monitor publicly accessible web resources according to user-defined schedules.
- Detect meaningful changes based on configurable monitoring rules.
- Maintain historical records of detected monitoring events.
- Deliver notifications through supported notification channels.
- Provide an intuitive dashboard for monitoring management.
- Establish a modular and extensible architecture capable of supporting future enhancements with minimal redesign.

---

## 1.4 Scope

### 1.4.1 In Scope

WatchTower Version 1.0 includes the following capabilities:

- User registration and authentication
- User profile management
- Monitoring task management
- Multiple monitoring rules per task
- Scheduled webpage monitoring
- HTML parsing and data extraction
- Change detection
- Monitoring snapshots
- History event recording
- Browser notifications
- Email notifications
- Dashboard and monitoring statistics
- Monitoring task search and filtering
- Configurable snapshot retention
- RESTful backend APIs
- Responsive web interface

---

### 1.4.2 Out of Scope

The following features are intentionally excluded from Version 1.0:

- AI-powered change analysis
- Browser extensions
- Android and iOS applications
- Shared workspaces
- Team collaboration
- Telegram notifications
- Discord notifications
- Slack notifications
- WhatsApp notifications
- OCR-based monitoring
- Visual screenshot comparison
- Predictive analytics
- Public monitoring templates
- Multi-language support

These features are documented in Chapter 6 (Future Scope) and are not considered part of the current project deliverables.

---

## 1.5 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| Monitoring Task | A user-defined configuration representing a webpage that should be monitored. |
| Monitoring Rule | A configurable condition that determines what aspect of a webpage should be evaluated. |
| Monitoring Snapshot | A record representing the observed state of a monitored webpage during a monitoring cycle. |
| History Event | A permanent record of a meaningful change detected by a monitoring rule. |
| Notification | A recorded attempt to inform a user about a detected monitoring event. |
| Notification Channel | A supported communication medium such as Browser Push or Email. |
| Retention Policy | Configuration specifying the number of monitoring snapshots retained before automatic cleanup. |

---

## 1.6 References

This document is based upon the following standards and technical references:

- IEEE 29148 – Systems and Software Engineering – Requirements Engineering
- FastAPI Documentation
- SQLAlchemy Documentation
- PostgreSQL Documentation
- Playwright Documentation
- BeautifulSoup4 Documentation

---

## 1.7 Document Conventions

The following requirement keywords are used throughout this specification.

| Keyword | Interpretation |
|-----------|----------------|
| **Shall** | Mandatory requirement |
| **Should** | Recommended implementation |
| **May** | Optional capability or future enhancement |

Requirement identifiers follow the conventions below:

| Prefix | Description |
|---------|-------------|
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| BR | Business Rule |
| UI | User Interface Requirement |
| API | API Requirement |
| AD | Architectural Decision |

These identifiers provide traceability between requirements, implementation, testing, and future revisions.

---

### Chapter Summary

This chapter establishes the purpose, objectives, and scope of WatchTower while defining the terminology and conventions used throughout this specification. Subsequent chapters build upon this foundation by describing the system architecture, functional behavior, interfaces, and quality requirements.

# 2. Overall Description

---

## Chapter Overview

This chapter provides a high-level description of WatchTower, its intended users, operating environment, major system functions, design constraints, and external dependencies. It establishes the overall context of the application before the detailed functional requirements presented in Chapter 3.

---

## 2.1 Product Perspective

WatchTower is a standalone web application designed to monitor publicly accessible web resources for meaningful changes. It follows a modular client-server architecture that separates user interaction, monitoring logic, scheduling, data persistence, and notification delivery into independent components with clearly defined responsibilities.

The system is designed with extensibility as a core architectural principle, enabling future support for additional monitoring rule types, notification providers, and user-facing features without requiring significant redesign of the existing application.

### High-Level System Components

The application consists of the following primary components:

| Component | Responsibility |
|-----------|----------------|
| Frontend | Provides the web-based user interface for interacting with the system. |
| Backend API | Processes requests, manages business logic, authentication, and data access. |
| Monitoring Engine | Executes scheduled monitoring tasks and evaluates monitoring rules. |
| Scheduler | Triggers monitoring tasks according to user-defined intervals. |
| Database | Stores users, monitoring tasks, rules, snapshots, history events, and notifications. |
| Notification Service | Delivers alerts through supported notification channels. |

The interaction between these components is documented in the Software Architecture Design Document.

---

## 2.2 Product Functions

WatchTower provides a configurable monitoring platform composed of the following functional modules.

### User Management

- User registration
- User authentication
- Profile management
- Password management
- Session management

---

### Monitoring Task Management

- Create monitoring tasks
- Update monitoring tasks
- Pause monitoring tasks
- Resume monitoring tasks
- Delete monitoring tasks
- Configure monitoring intervals
- Configure snapshot retention

---

### Monitoring Rule Management

- Create multiple monitoring rules per task
- Configure rule-specific settings
- Enable or disable rules
- Manage notification preferences

---

### Monitoring Engine

- Execute scheduled monitoring cycles
- Retrieve webpage content
- Extract monitored information
- Evaluate monitoring rules
- Detect meaningful changes
- Generate monitoring snapshots
- Record history events

---

### Notification Management

- Configure notification channels
- Browser notifications
- Email notifications
- Notification history

---

### Dashboard

- Monitoring overview
- Task status
- Recent activity
- Monitoring statistics
- Recent notifications

---

### History Management

- View detected changes
- Search history
- Filter history
- Review monitoring events

---

## 2.3 User Classes

WatchTower Version 1.0 supports two primary user classes.

### 2.3.1 Registered User

The Registered User represents the primary consumer of the application.

Registered users can:

- Register an account
- Sign in securely
- Create and manage monitoring tasks
- Configure monitoring rules
- Manage notification preferences
- View monitoring history
- Receive notifications
- Update their profile
- Delete their own monitoring tasks

Users are restricted to accessing resources associated with their own accounts.

---

### 2.3.2 System Administrator

The System Administrator is responsible for maintaining the application infrastructure rather than interacting with monitoring features.

Administrative responsibilities include:

- Application deployment
- Scheduler monitoring
- Database maintenance
- Log inspection
- Application configuration
- Backup and recovery operations

Version 1.0 does not include a dedicated administrator interface. Administrative tasks are performed directly through server-level tools.

---

## 2.4 Operating Environment

WatchTower Version 1.0 is designed to operate within the following environment.

### Backend

| Technology | Version |
|------------|---------|
| Python | 3.12+ |
| FastAPI | Latest Stable |
| SQLAlchemy | Latest Stable |
| Pydantic | Latest Stable |
| APScheduler | Latest Stable |

---

### Frontend

- HTML5
- CSS3
- JavaScript (ES6)
- Bootstrap 5.3.x

---

### Database

- PostgreSQL 16+

---

### Monitoring Technologies

- Playwright
- BeautifulSoup4

---

### Development Tools

- Visual Studio Code
- Git
- GitHub
- Postman

---

### Supported Platforms

The application is intended to run on:

- Windows
- Linux

Containerized deployment (Docker) may be introduced in future versions.

---

## 2.5 Design Constraints

The following constraints influence the design and implementation of WatchTower Version 1.0.

### Technology Constraints

The application shall use:

- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- APScheduler
- Playwright
- BeautifulSoup4

These technologies have been selected to provide a lightweight, modular, and scalable architecture.

---

### Browser Compatibility

The frontend shall support modern versions of:

- Google Chrome
- Microsoft Edge
- Mozilla Firefox

Internet Explorer is not supported.

---

### Security Constraints

The system shall:

- Store passwords using bcrypt hashing.
- Require authentication for protected resources.
- Enforce user-level resource isolation.
- Avoid exposing sensitive information through APIs or logs.

---

### Scalability Constraints

Version 1.0 is designed primarily for individual users and small-scale deployments.

Features such as distributed scheduling, horizontal scaling, load balancing, and multi-server execution are intentionally excluded from the current release.

---

## 2.6 Assumptions and Dependencies

The successful operation of WatchTower depends upon the following assumptions.

### Assumptions

- Users have reliable internet connectivity.
- Target webpages are publicly accessible.
- Target webpages permit automated retrieval.
- Users configure monitoring rules correctly.
- Email services remain available for notification delivery.

---

### External Dependencies

WatchTower relies on the following external components:

- PostgreSQL Database
- Playwright
- APScheduler
- SMTP Email Server
- Modern Web Browser

If one or more dependencies become unavailable, the affected functionality may be temporarily interrupted while the remainder of the application continues to operate where possible.

---

### Chapter Summary

This chapter described WatchTower from a high-level perspective, introducing its major functional modules, intended users, operating environment, design constraints, and external dependencies. The following chapter specifies the detailed functional requirements governing the behavior of each module.

# 3. Functional Requirements

---

## Chapter Overview

This chapter defines the functional behavior of WatchTower Version 1.0. It specifies the responsibilities and expected behavior of each major system module, along with the business rules governing their interaction.

Before describing individual modules, it is important to understand how the core monitoring workflow operates. The following lifecycle illustrates the sequence of operations performed during a typical monitoring cycle.

---

## 3.0 Monitoring Lifecycle Overview

### Purpose

The Monitoring Lifecycle describes the end-to-end execution flow of WatchTower, from the moment a user creates a monitoring task until a notification is delivered after a meaningful change is detected.

This lifecycle provides the conceptual foundation for the functional requirements defined throughout this chapter.

---

### Monitoring Workflow

```text
                    User
                     │
                     ▼
        Create Monitoring Task
                     │
                     ▼
       Configure Monitoring Rules
                     │
                     ▼
     Scheduler Triggers Monitoring
                     │
                     ▼
      Retrieve Target Webpage
                     │
                     ▼
      Extract Required Information
                     │
                     ▼
      Evaluate Monitoring Rules
                     │
                     ▼
     Create Monitoring Snapshot
                     │
                     ▼
        Was a Meaningful Change
             Detected?
          ┌───────────────┐
          │               │
         No              Yes
          │               │
          ▼               ▼
   Monitoring Ends   Create History Event
                          │
                          ▼
                Generate Notification(s)
                          │
                          ▼
                    Monitoring Ends
```

---

### Workflow Description

The normal execution sequence of a monitoring task is as follows:

1. A registered user creates a Monitoring Task by providing the target URL, monitoring interval, and other required configuration.

2. One or more Monitoring Rules are associated with the Monitoring Task. Each rule defines a specific condition that should be evaluated during monitoring.

3. The Scheduler periodically triggers active Monitoring Tasks according to their configured monitoring interval.

4. The Monitoring Engine retrieves the target webpage and extracts the information required by the configured Monitoring Rules.

5. Each active Monitoring Rule is evaluated independently.

6. After evaluation, the system creates a Monitoring Snapshot representing the observed state of the webpage during that monitoring cycle.

7. If no meaningful change is detected, the monitoring cycle completes without generating additional records.

8. If one or more Monitoring Rules detect a meaningful change, the system creates one or more History Events describing the detected changes.

9. Based on the user's configured Notification Preferences, the Notification Service generates notifications through the subscribed notification channels.

10. The monitoring cycle completes and the Scheduler waits until the next scheduled execution.

---

### Lifecycle Characteristics

The monitoring lifecycle follows these architectural principles:

- Each Monitoring Task represents a single target webpage.
- Multiple Monitoring Rules may be associated with a single Monitoring Task.
- Every successful monitoring cycle produces exactly one Monitoring Snapshot.
- A Monitoring Snapshot may generate zero, one, or multiple History Events.
- Notifications are generated only from History Events, never directly from Monitoring Snapshots.
- Monitoring failures affecting one task shall not interrupt monitoring of other active tasks.
- The lifecycle is designed to support future monitoring rule types and notification providers without requiring modifications to the core monitoring engine.

---

### Related Modules

The lifecycle described above is implemented through the following functional modules:

- Authentication Module
- Monitoring Task Module
- Monitoring Rule Module
- Monitoring Engine Module
- Monitoring Snapshot Module
- History Event Module
- Notification Module

The detailed behavior of each module is specified in the following sections.

## 3.1 Authentication Module

---

### Purpose

The Authentication Module is responsible for verifying user identity and protecting access to WatchTower. It ensures that only authenticated users can access protected resources while maintaining the confidentiality and integrity of user credentials.

Authentication serves as the entry point to all user-specific functionality within the application.

---

### Responsibilities

This module is responsible for:

- User registration
- User authentication
- Secure password storage
- Session management
- Access control for protected resources

---

### Functional Requirements

#### FR-AUTH-001 – User Registration

The system shall allow a new user to create an account by providing:

- Username
- Email Address
- Password

Registration shall be completed only after successful validation of the submitted information.

---

#### FR-AUTH-002 – Unique Email Address

The system shall ensure that every registered email address is unique.

Registration attempts using an existing email address shall be rejected with an appropriate validation message.

---

#### FR-AUTH-003 – Password Security

The system shall hash user passwords using the bcrypt hashing algorithm before storing them in the database.

Plain-text passwords shall never be stored, logged, or returned by the system.

---

#### FR-AUTH-004 – User Login

The system shall authenticate users using their registered email address and password.

Successful authentication shall create a secure authenticated session.

---

#### FR-AUTH-005 – Authentication Token

Following successful authentication, the system shall issue a JSON Web Token (JWT) to authorize subsequent requests to protected API endpoints.

---

#### FR-AUTH-006 – Logout

The system shall allow authenticated users to terminate their active session.

Following logout, previously issued authentication tokens shall no longer grant access to protected resources.

---

#### FR-AUTH-007 – Invalid Credentials

The system shall reject authentication requests containing invalid credentials.

The response shall not disclose whether the username or password caused the authentication failure.

---

#### FR-AUTH-008 – Protected Resources

Protected API endpoints shall require successful authentication before processing requests.

Unauthorized requests shall receive an appropriate HTTP error response.

---

#### FR-AUTH-009 – User Isolation

Authenticated users shall only access resources associated with their own account.

Attempts to access another user's resources shall be denied.

---

#### FR-AUTH-010 – Authentication Errors

The system shall return meaningful validation messages for authentication failures while avoiding disclosure of sensitive implementation details.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-AUTH-001 | Every registered email address shall be unique. |
| BR-AUTH-002 | Passwords shall never be stored in plain text. |
| BR-AUTH-003 | Authentication is required before accessing protected resources. |
| BR-AUTH-004 | Each authenticated request shall be associated with exactly one registered user. |

---

### Related Modules

This module directly interacts with:

- User Management Module
- Dashboard Module
- Monitoring Task Module
- Notification Module

All user-specific operations depend on successful authentication.

---

### Module Notes

Authentication is implemented once and shared across the entire application. Future authentication mechanisms such as OAuth2 or Single Sign-On (SSO) may be introduced without affecting the functional behavior described in this specification.

## 3.2 User Management Module

---

### Purpose

The User Management Module enables authenticated users to manage their personal account information and application preferences. It ensures that users retain full control over their account while maintaining data integrity and enforcing appropriate access restrictions.

---

### Responsibilities

This module is responsible for:

- Viewing user profile information
- Updating account details
- Changing passwords
- Maintaining user account metadata
- Protecting user-specific information

---

### Functional Requirements (7)

#### FR-USER-001 – View Profile

The system shall allow authenticated users to view their profile information.

---

#### FR-USER-002 – Update Username

The system shall allow authenticated users to update their username.

---

#### FR-USER-003 – Update Email Address

The system shall allow authenticated users to update their registered email address, provided the new email address is not already associated with another account.

---

#### FR-USER-004 – Change Password

The system shall allow authenticated users to change their password after successfully verifying their current password.

---

#### FR-USER-005 – Account Isolation

The system shall prevent users from modifying another user's account information.

---

#### FR-USER-006 – Account Creation Timestamp

The system shall maintain the creation timestamp for every registered account.

---

#### FR-USER-007 – Last Updated Timestamp

The system shall maintain the timestamp of the most recent profile modification.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-USER-001 | Every registered email address shall remain unique throughout the system. |
| BR-USER-002 | Passwords shall never be exposed through API responses. |
| BR-USER-003 | Users may modify only their own profile information. |

---

### Related Modules

- Authentication Module
- Dashboard Module
- Notification Module

---

### Module Notes

User profile information represents account-level configuration and is independent of monitoring task configuration. Future versions may extend this module to support profile images, account verification, and multi-factor authentication.

## 3.3 Dashboard Module

---

### Purpose

The Dashboard Module provides users with a centralized overview of their monitoring activities. It serves as the application's primary workspace after authentication by presenting monitoring status, recent activity, and quick access to commonly used operations.

---

### Responsibilities

This module is responsible for:

- Displaying monitoring statistics
- Summarizing monitoring activity
- Providing quick navigation
- Highlighting recent notifications
- Presenting system status

---

### Functional Requirements (9)

#### FR-DASH-001 – Monitoring Summary

The system shall display the total number of monitoring tasks created by the authenticated user.

---

#### FR-DASH-002 – Active Monitoring Tasks

The system shall display the number of currently active monitoring tasks.

---

#### FR-DASH-003 – Paused Monitoring Tasks

The system shall display the number of paused monitoring tasks.

---

#### FR-DASH-004 – Recent Monitoring Events

The system shall display recently detected monitoring events.

---

#### FR-DASH-005 – Recent Notifications

The system shall display the most recent notifications generated for the authenticated user.

---

#### FR-DASH-006 – Task Navigation

The system shall allow users to navigate directly from the dashboard to any monitoring task.

---

#### FR-DASH-007 – Dynamic Updates

The dashboard should refresh displayed information without requiring a complete page reload where technically feasible.

---

#### FR-DASH-008 – Last Monitoring Status

The system shall display the timestamp of the last successful monitoring execution for each monitoring task.

---

#### FR-DASH-009 – Monitoring Alerts

The dashboard shall highlight monitoring tasks that have experienced repeated failures or require user attention.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-DASH-001 | Dashboard information shall display only data belonging to the authenticated user. |
| BR-DASH-002 | Dashboard statistics shall be calculated using current system data. |

---

### Related Modules

- Monitoring Task Module
- Monitoring Snapshot Module
- History Event Module
- Notification Module

---

### Module Notes

The dashboard is intended to provide an operational overview rather than detailed monitoring analysis. Detailed information is available through the corresponding functional modules.

## 3.4 Monitoring Task Module

---

### Purpose

The Monitoring Task Module represents the core business entity of WatchTower. It enables users to define web resources that should be monitored and acts as the central point around which all monitoring activities are organized.

Each Monitoring Task represents a single target URL and serves as the aggregate root for its associated Monitoring Rules, Monitoring Snapshots, History Events, and Notifications.

---

### Responsibilities

This module is responsible for:

- Creating monitoring tasks
- Managing task configuration
- Controlling the monitoring lifecycle
- Scheduling monitoring execution
- Maintaining monitoring metadata
- Managing snapshot retention policies

---

### Functional Requirements (14)

#### FR-TASK-001 – Create Monitoring Task

The system shall allow authenticated users to create a Monitoring Task.

Each Monitoring Task shall represent a single publicly accessible target URL.

---

#### FR-TASK-002 – Required Information

A Monitoring Task shall contain the following information:

- Task Name
- Target URL
- Monitoring Interval
- Status
- Snapshot Retention Limit

Additional metadata may be maintained internally by the system.

---

#### FR-TASK-003 – URL Validation

The system shall validate the submitted URL before creating the Monitoring Task.

Invalid or unsupported URLs shall be rejected with an appropriate validation message.

---

#### FR-TASK-004 – Update Monitoring Task

The system shall allow authenticated users to modify the configuration of an existing Monitoring Task.

Changes shall take effect during the next scheduled monitoring cycle unless otherwise specified.

---

#### FR-TASK-005 – Pause Monitoring

The system shall allow users to temporarily pause a Monitoring Task without deleting its associated configuration or historical data.

Paused Monitoring Tasks shall not be executed by the Monitoring Engine.

---

#### FR-TASK-006 – Resume Monitoring

The system shall allow users to resume a previously paused Monitoring Task.

Monitoring shall continue according to the configured schedule.

---

#### FR-TASK-007 – Delete Monitoring Task

The system shall allow users to permanently delete a Monitoring Task.

Deletion shall permanently remove all dependent monitoring data associated with that task.

---

#### FR-TASK-008 – Monitoring Interval

The system shall support configurable monitoring intervals.

Version 1.0 shall support predefined monitoring intervals configured by the application.

---

#### FR-TASK-009 – Task Status

A Monitoring Task shall maintain one of the following states:

- Active
- Paused
- Disabled *(Reserved for future administrative functionality)*

---

#### FR-TASK-010 – Ownership

Users shall only view or modify Monitoring Tasks that belong to their own account.

---

#### FR-TASK-011 – Creation Timestamp

The system shall record the creation date and time of every Monitoring Task.

---

#### FR-TASK-012 – Last Execution

The system shall record the timestamp of the most recent monitoring execution.

---

#### FR-TASK-013 – Next Scheduled Execution

The system shall maintain the next scheduled execution time for each active Monitoring Task.

---

#### FR-TASK-014 – Snapshot Retention

The system shall allow users to configure the maximum number of Monitoring Snapshots retained for each Monitoring Task.

Snapshots exceeding the configured retention limit shall be automatically removed according to the retention policy.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-TASK-001 | Every Monitoring Task shall monitor exactly one target URL. |
| BR-TASK-002 | A Monitoring Task may contain one or more Monitoring Rules. |
| BR-TASK-003 | Deleting a Monitoring Task shall permanently remove all associated Monitoring Rules, Monitoring Snapshots, History Events, Notification Preferences, and Notifications. |
| BR-TASK-004 | Only Active Monitoring Tasks shall be eligible for scheduled execution. |

---

### Related Modules

This module directly interacts with:

- Monitoring Rule Module
- Monitoring Engine Module
- Monitoring Snapshot Module
- History Event Module
- Notification Module

---

### Module Notes

The Monitoring Task is the primary aggregate root within the WatchTower domain model.

All monitoring-related information is organized around the Monitoring Task, making it the central entity responsible for maintaining the consistency of monitoring operations.

Future versions may extend this module with features such as task grouping, tagging, folder organization, and bulk task management without altering its core responsibility.

## 3.5 Monitoring Rule Module

---

### Purpose

The Monitoring Rule Module defines **what** should be monitored within a Monitoring Task and **how** meaningful changes should be evaluated.

Each Monitoring Rule represents an independent monitoring condition. Multiple rules may be associated with the same Monitoring Task, enabling a single webpage to be monitored for different types of changes simultaneously.

---

### Responsibilities

This module is responsible for:

- Defining monitoring conditions
- Managing rule configuration
- Enabling or disabling individual rules
- Supporting multiple monitoring strategies
- Triggering History Events when meaningful changes are detected

---

### Functional Requirements (10)

#### FR-RULE-001 – Create Monitoring Rule

The system shall allow users to create one or more Monitoring Rules for a Monitoring Task.

---

#### FR-RULE-002 – Rule Association

Each Monitoring Rule shall belong to exactly one Monitoring Task.

A Monitoring Task may contain multiple Monitoring Rules.

---

#### FR-RULE-003 – Rule Configuration

Each Monitoring Rule shall maintain the following information:

- Rule Type
- Rule Status
- Target Configuration
- Optional Description

The required configuration may vary depending on the selected Rule Type.

---

#### FR-RULE-004 – Update Rule

The system shall allow users to modify the configuration of an existing Monitoring Rule.

Configuration changes shall take effect during the next monitoring cycle.

---

#### FR-RULE-005 – Enable or Disable Rule

The system shall allow users to enable or disable Monitoring Rules independently without affecting other rules associated with the same Monitoring Task.

---

#### FR-RULE-006 – Supported Rule Types

Version 1.0 shall support multiple configurable monitoring rule types.

The specific rule types supported by the application are implementation-dependent and may be extended in future versions without altering the Monitoring Engine.

---

#### FR-RULE-007 – Independent Rule Evaluation

During each monitoring cycle, every active Monitoring Rule associated with a Monitoring Task shall be evaluated independently.

---

#### FR-RULE-008 – Change Detection

When a Monitoring Rule detects a meaningful change, the system shall create a corresponding History Event.

---

#### FR-RULE-009 – Disabled Rules

Disabled Monitoring Rules shall not participate in monitoring or change evaluation.

---

#### FR-RULE-010 – Rule Deletion

The system shall allow users to delete individual Monitoring Rules without affecting other rules associated with the same Monitoring Task.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-RULE-001 | A Monitoring Task shall contain at least one active Monitoring Rule before monitoring can begin. |
| BR-RULE-002 | Multiple Monitoring Rules may generate History Events during the same monitoring cycle. |
| BR-RULE-003 | Each Monitoring Rule maintains its own notification configuration. |
| BR-RULE-004 | Monitoring Rules operate independently of one another. |

---

### Related Modules

- Monitoring Task Module
- Monitoring Engine Module
- History Event Module
- Notification Module

---

### Design Considerations

Monitoring Rules intentionally encapsulate monitoring logic instead of embedding it within the Monitoring Task.

This separation allows WatchTower to support new monitoring strategies in future versions without modifying the core monitoring engine or the Monitoring Task model.

The Monitoring Rule is therefore the primary extension point for future monitoring capabilities.

## 3.6 Monitoring Engine Module

---

### Purpose

The Monitoring Engine is the core processing component of WatchTower. It is responsible for executing scheduled monitoring tasks, retrieving target webpages, evaluating monitoring rules, recording monitoring observations, and initiating subsequent system actions when meaningful changes are detected.

The Monitoring Engine operates autonomously and forms the operational backbone of the application.

---

### Responsibilities

This module is responsible for:

- Executing scheduled monitoring tasks
- Retrieving webpage content
- Coordinating rule evaluation
- Creating monitoring snapshots
- Detecting meaningful changes
- Recording monitoring events
- Initiating notification delivery
- Updating monitoring metadata

---

### Functional Requirements (14)

#### FR-ENGINE-001 – Scheduled Execution

The system shall execute active Monitoring Tasks according to their configured monitoring schedule.

---

#### FR-ENGINE-002 – Task Eligibility

Only Monitoring Tasks in the **Active** state shall be eligible for execution.

Paused or disabled tasks shall be ignored by the Monitoring Engine.

---

#### FR-ENGINE-003 – Retrieve Target Resource

For each execution, the Monitoring Engine shall retrieve the target webpage associated with the Monitoring Task.

---

#### FR-ENGINE-004 – Resource Availability

The Monitoring Engine shall determine whether the target resource was successfully retrieved before evaluating Monitoring Rules.

If retrieval fails, the monitoring cycle shall terminate gracefully for that task.

---

#### FR-ENGINE-005 – Information Extraction

The Monitoring Engine shall extract only the information required by the active Monitoring Rules associated with the Monitoring Task.

---

#### FR-ENGINE-006 – Rule Evaluation

Each active Monitoring Rule shall be evaluated independently during the monitoring cycle.

The outcome of one Monitoring Rule shall not influence the evaluation of another.

---

#### FR-ENGINE-007 – Monitoring Snapshot

After successful rule evaluation, the system shall create a Monitoring Snapshot representing the observed state of the monitored resource.

---

#### FR-ENGINE-008 – Change Detection

If one or more Monitoring Rules detect a meaningful change, the system shall generate the corresponding History Event(s).

---

#### FR-ENGINE-009 – Notification Trigger

The Monitoring Engine shall initiate notification processing only after the successful creation of a History Event.

---

#### FR-ENGINE-010 – Execution Metadata

The system shall update the Monitoring Task with the latest execution information, including:

- Last Execution Time
- Next Scheduled Execution Time
- Execution Status

---

#### FR-ENGINE-011 – Independent Execution

A failure occurring during the execution of one Monitoring Task shall not interrupt the execution of other active Monitoring Tasks.

---

#### FR-ENGINE-012 – Monitoring Completion

Every monitoring cycle shall terminate in one of the following outcomes:

- Successful execution without detected changes.
- Successful execution with detected changes.
- Failed execution.

---

#### FR-ENGINE-013 – Error Logging

Unexpected execution failures shall be recorded for diagnostic purposes.

---

#### FR-ENGINE-014 – Lifecycle Continuity

Upon completion of a monitoring cycle, the Monitoring Engine shall return control to the Scheduler and await the next scheduled execution.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-ENGINE-001 | Every successful monitoring cycle shall produce exactly one Monitoring Snapshot. |
| BR-ENGINE-002 | Monitoring Rules shall always be evaluated independently. |
| BR-ENGINE-003 | History Events shall only be created when meaningful changes are detected. |
| BR-ENGINE-004 | Notifications shall only be initiated after a History Event has been successfully recorded. |
| BR-ENGINE-005 | Failure of one Monitoring Task shall not affect other Monitoring Tasks. |

---

### Related Modules

- Monitoring Task Module
- Monitoring Rule Module
- Monitoring Snapshot Module
- History Event Module
- Notification Module

---

### Design Considerations

The Monitoring Engine coordinates the execution of monitoring activities but intentionally avoids embedding rule-specific business logic.

Instead, rule evaluation is delegated to individual Monitoring Rules, allowing the Monitoring Engine to remain generic and extensible.

This separation enables future monitoring capabilities to be introduced without modifying the engine's core workflow.

## 3.7 Monitoring Snapshot Module

---

### Purpose

The Monitoring Snapshot Module records the observed state of a monitored resource during each successful monitoring cycle.

Snapshots provide a lightweight historical record of monitoring observations and act as the reference point from which meaningful changes are identified. They represent system observations rather than business events and therefore remain independent of notification and reporting logic.

---

### Responsibilities

This module is responsible for:

- Recording monitoring observations
- Preserving execution metadata
- Supporting change comparison
- Applying snapshot retention policies
- Providing historical monitoring context

---

### Functional Requirements (6)

#### FR-SNAPSHOT-001 – Snapshot Creation

The system shall create exactly one Monitoring Snapshot for every successful monitoring cycle.

---

#### FR-SNAPSHOT-002 – Snapshot Association

Each Monitoring Snapshot shall be associated with exactly one Monitoring Task.

---

#### FR-SNAPSHOT-003 – Snapshot Information

Each Monitoring Snapshot shall record:

- Observation Timestamp
- HTTP Response Status
- Response Time
- Monitoring Metadata

Additional implementation-specific information may be recorded where necessary.

---

#### FR-SNAPSHOT-004 – Snapshot Retention

Monitoring Snapshots shall be retained according to the retention policy configured for the associated Monitoring Task.

---

#### FR-SNAPSHOT-005 – Snapshot Cleanup

Snapshots exceeding the configured retention limit shall be removed automatically without affecting permanent monitoring history.

---

#### FR-SNAPSHOT-006 – Snapshot Retrieval

The system shall allow authorized components to retrieve Monitoring Snapshots for comparison and historical reference.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-SNAPSHOT-001 | Every successful monitoring cycle shall generate exactly one Monitoring Snapshot. |
| BR-SNAPSHOT-002 | Monitoring Snapshots represent observations, not business events. |
| BR-SNAPSHOT-003 | Snapshot cleanup shall never remove History Events. |

---

### Related Modules

- Monitoring Engine Module
- History Event Module
- Monitoring Task Module

---

### Design Considerations

Monitoring Snapshots are intentionally designed as temporary operational records.

Business information that must remain permanently available is stored within History Events rather than Monitoring Snapshots. This separation allows historical monitoring information to remain available even after older snapshots have been removed according to the configured retention policy.

## 3.8 History Event Module

---

### Purpose

The History Event Module permanently records meaningful monitoring outcomes detected during monitoring execution.

Unlike Monitoring Snapshots, which represent observations, History Events represent significant business events that provide users with an auditable history of detected changes.

History Events also serve as the source for notification generation.

---

### Responsibilities

This module is responsible for:

- Recording detected changes
- Maintaining permanent monitoring history
- Supporting history search and filtering
- Triggering notification generation
- Preserving audit information

---

### Functional Requirements (8)

#### FR-HISTORY-001 – Event Creation

The system shall create a History Event whenever one or more Monitoring Rules detect a meaningful change.

---

#### FR-HISTORY-002 – Snapshot Reference

Each History Event shall reference the Monitoring Snapshot from which it originated.

---

#### FR-HISTORY-003 – Rule Reference

Each History Event shall identify the Monitoring Rule responsible for detecting the change.

---

#### FR-HISTORY-004 – Event Information

Each History Event shall record:

- Event Type
- Previous Value
- Current Value
- Detection Timestamp

---

#### FR-HISTORY-005 – Event Retrieval

The system shall allow authenticated users to browse their monitoring history.

---

#### FR-HISTORY-006 – History Filtering

Users shall be able to filter History Events using one or more supported search criteria.

---

#### FR-HISTORY-007 – Event Integrity

History Events shall remain unchanged after creation.

---

#### FR-HISTORY-008 – Event Persistence

History Events shall remain available even after their associated Monitoring Snapshots have been removed through retention policies.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-HISTORY-001 | History Events are immutable. |
| BR-HISTORY-002 | Every History Event shall originate from exactly one Monitoring Snapshot. |
| BR-HISTORY-003 | Notifications shall be generated from History Events rather than Monitoring Snapshots. |

---

### Related Modules

- Monitoring Snapshot Module
- Monitoring Engine Module
- Notification Module

---

### Design Considerations

History Events form the permanent audit trail of WatchTower.

Because they represent business events rather than operational observations, they remain available independently of Monitoring Snapshot retention policies.

This separation supports efficient storage management while preserving complete monitoring history.

## 3.9 Notification Module

---

### Purpose

The Notification Module is responsible for informing users whenever a meaningful monitoring event is detected.

It manages notification preferences, determines the appropriate notification channels, delivers notifications, and maintains a history of notification activities.

Notifications are generated only after a History Event has been successfully recorded, ensuring that users are informed exclusively about significant monitoring outcomes.

---

### Responsibilities

This module is responsible for:

- Managing notification preferences
- Managing notification channels
- Delivering notifications
- Recording notification history
- Tracking notification delivery status

---

### Functional Requirements (11)

#### FR-NOTIFY-001 – Notification Preferences

The system shall allow users to configure notification preferences for each Monitoring Rule independently.

---

#### FR-NOTIFY-002 – Notification Channels

Version 1.0 shall support multiple notification channels.

Supported notification channels are implementation-specific and may be extended in future versions without modifying the core monitoring workflow.

---

#### FR-NOTIFY-003 – Notification Generation

The system shall generate notifications only after a History Event has been successfully created.

---

#### FR-NOTIFY-004 – Channel Selection

The system shall deliver notifications only through the notification channels enabled for the corresponding Monitoring Rule.

---

#### FR-NOTIFY-005 – Notification Information

Each Notification shall record:

- Notification Timestamp
- Notification Channel
- Delivery Status
- Related History Event

Additional delivery metadata may be recorded where necessary.

---

#### FR-NOTIFY-006 – Notification History

The system shall maintain a history of generated notifications.

---

#### FR-NOTIFY-007 – Read Status

Authenticated users shall be able to mark notifications as read.

---

#### FR-NOTIFY-008 – Notification Removal

Authenticated users shall be able to delete notification records associated with their own account.

---

#### FR-NOTIFY-009 – Delivery Failure

Failure to deliver a notification through one notification channel shall not prevent delivery through other configured channels.

---

#### FR-NOTIFY-010 – Notification Retry

The system may retry failed notification deliveries according to the configured notification strategy.

---

#### FR-NOTIFY-011 – User Isolation

Users shall only access notifications generated for their own Monitoring Tasks.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-NOTIFY-001 | Notifications shall always originate from a History Event. |
| BR-NOTIFY-002 | Notification preferences are evaluated independently for each Monitoring Rule. |
| BR-NOTIFY-003 | Notification delivery failures shall not interrupt monitoring execution. |
| BR-NOTIFY-004 | Every notification shall reference exactly one History Event. |

---

### Related Modules

- History Event Module
- Monitoring Rule Module
- User Management Module

---

### Design Considerations

Notification configuration is intentionally separated from notification delivery.

This design enables additional notification providers, such as Telegram, Discord, Slack, or WhatsApp, to be integrated in future versions without modifying the Monitoring Engine or History Event modules.

The Notification Module therefore acts as the abstraction layer between monitoring outcomes and external communication services.

## 3.10 Settings Module

---

### Purpose

The Settings Module allows users to configure application-level preferences that influence the behavior of WatchTower without affecting its core functionality.

---

### Responsibilities

This module is responsible for:

- Managing application preferences
- Managing default notification settings
- Managing user-specific configuration

---

### Functional Requirements (5)

#### FR-SETTINGS-001

The system shall allow authenticated users to view their application settings.

---

#### FR-SETTINGS-002

The system shall allow users to update supported application preferences.

---

#### FR-SETTINGS-003

Updated settings shall take effect immediately unless otherwise specified.

---

#### FR-SETTINGS-004

The system shall validate all settings before saving changes.

---

#### FR-SETTINGS-005

Users shall only modify settings associated with their own account.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-SETTINGS-001 | Application settings shall not modify historical monitoring records. |
| BR-SETTINGS-002 | Invalid configuration values shall be rejected before being persisted. |

---

### Related Modules

- User Management Module
- Notification Module

---

### Design Considerations

The Settings Module stores user-specific preferences rather than system-wide configuration.

Administrative configuration is intentionally outside the scope of Version 1.0.

## 3.11 Error Handling Module

---

### Purpose

The Error Handling Module ensures that unexpected failures are managed gracefully without compromising application stability or interrupting unrelated monitoring activities.

---

### Responsibilities

This module is responsible for:

- Detecting application errors
- Logging unexpected failures
- Providing meaningful error responses
- Maintaining monitoring continuity

---

### Functional Requirements (8)

#### FR-ERROR-001

The system shall detect and log unexpected runtime errors.

---

#### FR-ERROR-002

Monitoring failures affecting one Monitoring Task shall not interrupt monitoring of other active Monitoring Tasks.

---

#### FR-ERROR-003

The system shall return meaningful validation messages for recoverable user errors.

---

#### FR-ERROR-004

Internal implementation details shall not be exposed through error responses.

---

#### FR-ERROR-005

The system shall return appropriate HTTP status codes for all API responses.

---

#### FR-ERROR-006

Unexpected application failures shall be recorded for diagnostic purposes.

---

#### FR-ERROR-007

The Monitoring Scheduler shall continue operating after recoverable failures.

---

#### FR-ERROR-008

Failed monitoring executions shall be reflected in the Monitoring Task execution status.

---

### Business Rules

| ID | Business Rule |
|----|---------------|
| BR-ERROR-001 | Recoverable failures shall not terminate the Monitoring Scheduler. |
| BR-ERROR-002 | All unexpected server-side exceptions shall be recorded in the application logs. |

---

### Related Modules

All functional modules.

---

### Design Considerations

Error handling is implemented as a cross-cutting concern shared across the entire application.

The primary objective is to maximize application availability while providing sufficient diagnostic information for troubleshooting.

# 4. External Interface Requirements

---

## Chapter Overview

This chapter defines the interfaces through which WatchTower communicates with users, external systems, and supporting infrastructure. These interfaces establish the boundaries between WatchTower and its environment while ensuring consistent interaction across all system components.

---

## 4.1 User Interface

### Overview

WatchTower shall provide a responsive web-based user interface that enables users to interact with all supported system functionality through a modern web browser.

The user interface shall prioritize simplicity, consistency, and ease of navigation while presenting monitoring information in a clear and organized manner.

---

### User Interface Components

Version 1.0 shall provide interfaces for:

- User Authentication
- Dashboard
- Monitoring Task Management
- Monitoring Rule Management
- Notification Center
- Monitoring History
- User Profile
- Application Settings

---

### User Interface Requirements

#### UI-001

The interface shall be responsive and usable on desktop and laptop devices.

---

#### UI-002

Navigation shall remain consistent throughout the application.

---

#### UI-003

The interface shall provide immediate visual feedback for user actions where appropriate.

---

#### UI-004

Validation errors shall be presented in a clear and understandable manner.

---

#### UI-005

Monitoring information shall be presented using structured tables, cards, or other appropriate interface components.

---

## 4.2 API Interface

### Overview

WatchTower exposes RESTful APIs that enable communication between the frontend and backend components.

All protected endpoints require authentication.

---

### API Requirements

The backend shall provide APIs for:

- Authentication
- User Management
- Monitoring Tasks
- Monitoring Rules
- Monitoring Snapshots
- History Events
- Notifications
- Settings

---

#### API-001

All API requests and responses shall use JSON.

---

#### API-002

Protected endpoints shall require JWT authentication.

---

#### API-003

The API shall return appropriate HTTP status codes.

---

#### API-004

API responses shall follow a consistent response structure.

---

## 4.3 Database Interface

The application shall communicate with PostgreSQL exclusively through SQLAlchemy ORM.

Direct database access from the frontend shall not be permitted.

---

## 4.4 Notification Interfaces

Version 1.0 supports:

- Browser Push Notifications
- Email Notifications

The notification subsystem shall be designed to support additional providers in future releases without affecting existing monitoring functionality.

---

### Chapter Summary

This chapter defines the external interfaces used by WatchTower for user interaction, API communication, database access, and notification delivery.

# 5. Non-Functional Requirements

---

## Chapter Overview

This chapter specifies the quality attributes that define how WatchTower performs rather than what functionality it provides.

---

## 5.1 Performance

### NFR-PERF-001

The application shall support concurrent execution of multiple monitoring tasks.

---

### NFR-PERF-002

Dashboard information should be displayed with minimal latency under normal operating conditions.

---

### NFR-PERF-003

Monitoring operations shall execute independently to minimize the impact of slow or unresponsive target websites.

---

## 5.2 Reliability

### NFR-REL-001

Failures affecting one monitoring task shall not interrupt monitoring of other active tasks.

---

### NFR-REL-002

Notification delivery failures shall not interrupt monitoring execution.

---

### NFR-REL-003

Unexpected failures shall be recorded for diagnostic purposes.

---

## 5.3 Security

### NFR-SEC-001

Passwords shall be stored only as bcrypt hashes.

---

### NFR-SEC-002

Protected resources shall require authentication.

---

### NFR-SEC-003

Users shall access only their own resources.

---

### NFR-SEC-004

Sensitive information shall never be exposed through API responses or application logs.

---

## 5.4 Scalability

The application architecture shall support future expansion through modular design.

Future monitoring rule types, notification providers, and user-facing features shall be introduced without requiring significant architectural redesign.

---

## 5.5 Maintainability

The application shall adopt a modular architecture with clearly separated responsibilities.

The codebase shall be organized to facilitate future maintenance and extension.

---

## 5.6 Usability

The user interface shall remain simple, consistent, and intuitive.

Users shall perform common monitoring operations without requiring technical knowledge.

---

## 5.7 Portability

WatchTower shall support deployment on Windows and Linux operating systems.

---

## 5.8 Logging

The application shall maintain logs for:

- Monitoring execution
- System errors
- Notification failures
- Scheduler activity

---

### Chapter Summary

These quality requirements ensure that WatchTower remains secure, reliable, maintainable, and scalable while providing a positive user experience.

# 6. Future Scope

---

## Chapter Overview

This chapter documents enhancements intentionally excluded from Version 1.0 while remaining compatible with the current architecture.

---

## Planned Enhancements

### Artificial Intelligence

- AI-assisted change summarization
- Intelligent change classification
- Notification prioritization

---

### Additional Notification Providers

- Telegram
- Discord
- Slack
- Microsoft Teams
- WhatsApp
- SMS

---

### Browser Extension

Users may create monitoring tasks directly from supported web browsers.

---

### Mobile Application

Native Android and iOS applications.

---

### Visual Monitoring

- Screenshot comparison
- Layout monitoring
- Image monitoring

---

### Collaboration

- Shared workspaces
- Team monitoring
- Role-based permissions

---

### Advanced Analytics

- Response-time analytics
- Monitoring trends
- Notification analytics
- Dashboard insights

---

### Public Templates

Predefined monitoring templates for commonly monitored websites.

---

### Chapter Summary

The modular architecture adopted in Version 1.0 enables these enhancements without requiring significant redesign of the application's core components.

# 7. Appendices

---

## Appendix A — Glossary

(Existing glossary remains.)

---

## Appendix B — Technology Stack

(Existing technology stack remains.)

---

## Appendix C — Supporting Documents

This Software Requirements Specification is complemented by:

- Software Architecture Design Document
- Database Design Document
- API Specification
- Test Plan
- Deployment Guide
- User Guide

---

## Appendix D — Architectural Decisions

(Existing Architectural Decisions remain.)

---

## Appendix E — Project Limitations

The following limitations apply to Version 1.0.

- Monitoring is limited to publicly accessible web resources.
- Some websites may restrict automated access.
- Dynamic webpage changes may require additional extraction strategies.
- Notification delivery depends on the availability of external services.
- Large-scale distributed monitoring is outside the scope of Version 1.0.

---

## Appendix F — Requirement Traceability Matrix

| Requirement | Module | Verification |
|------------|--------|--------------|
| FR-AUTH-001 | Authentication | Functional Testing |
| FR-TASK-001 | Monitoring Task | Functional Testing |
| FR-RULE-001 | Monitoring Rule | Functional Testing |
| FR-ENGINE-001 | Monitoring Engine | Integration Testing |
| FR-HISTORY-001 | History Event | Integration Testing |
| FR-NOTIFY-001 | Notification | Functional Testing |

(The complete matrix will be expanded during the testing phase.)

---

## Document Conclusion

This Software Requirements Specification establishes the functional and non-functional requirements for WatchTower Version 1.0.

The document serves as the baseline for architecture design, database design, API specification, implementation, testing, deployment, and future maintenance.

All future revisions to WatchTower shall be evaluated against the requirements defined in this specification.
