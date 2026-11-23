# WatchTower

### Monitor. Detect. Notify.

WatchTower is a web-based website monitoring application designed to track publicly accessible websites, detect meaningful changes, and notify users when those changes occur.

Users can create monitoring tasks, configure custom monitoring rules, review detected changes, and manage notifications through a centralized dashboard.

The application follows a modular, layered architecture that separates API handling, business logic, monitoring execution, database operations, and notification delivery.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create a Virtual Environment](#2-create-a-virtual-environment)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Install Playwright Browser](#4-install-playwright-browser)
  - [5. Configure PostgreSQL](#5-configure-postgresql)
  - [6. Configure Environment Variables](#6-configure-environment-variables)
  - [7. Run Database Migrations](#7-run-database-migrations)
  - [8. Start the Backend](#8-start-the-backend)
  - [9. Start the Frontend](#9-start-the-frontend)
- [Accessing the Application](#accessing-the-application)
- [API Overview](#api-overview)
- [Monitoring Workflow](#monitoring-workflow)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Configuration Reference](#configuration-reference)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [Documentation](#documentation)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### User Authentication
- User registration and login.
- JWT-based authentication.
- Secure password hashing.
- Token revocation during logout.
- User profile management.

### Website Monitoring
- Create and manage website monitoring tasks.
- Configure monitoring intervals.
- Pause and resume monitoring tasks.
- Delete monitoring tasks.
- Automated background monitoring.

### Monitoring Rules
- Create custom monitoring rules.
- Configure rule-specific conditions.
- Manage rules associated with monitoring tasks.
- Evaluate website content against configured conditions.

### Change Detection
- Retrieve and extract website information.
- Evaluate extracted information against configured rules.
- Detect meaningful changes.
- Maintain monitoring snapshots and history events.

### Notification Management
- Email notification support through SMTP.
- Browser push notification support.
- Manage notification preferences.
- View and manage notification records.

### Dashboard
- Centralized monitoring overview.
- Monitoring task management.
- Recent monitoring activity.
- Notification management.

---

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Frontend | HTML5, CSS3, JavaScript (ES6) |
| UI Framework | Bootstrap |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Database Migrations | Alembic |
| Background Scheduler | APScheduler |
| Web Scraping | Playwright, BeautifulSoup4 |
| API Server | Uvicorn |
| Authentication | JWT |
| Testing | Pytest |

---

## Architecture

WatchTower follows a layered architecture with clearly separated responsibilities.

```text
                         USER
                           |
                           v
                 +-------------------+
                 |     Frontend      |
                 |   HTML/CSS/JS     |
                 +-------------------+
                           |
                           v
                 +-------------------+
                 |     FastAPI       |
                 |     REST API      |
                 +-------------------+
                           |
                           v
                 +-------------------+
                 |   Service Layer   |
                 |   Business Logic  |
                 +-------------------+
                           |
              +------------+------------+
              |                         |
              v                         v
     +------------------+      +------------------+
     | Repository Layer |      | Monitoring Engine|
     | Database Access  |      | Change Detection |
     +------------------+      +------------------+
              |                         |
              v                         v
     +------------------+      +------------------+
     |   PostgreSQL     |      | Notification     |
     |    Database      |      |    Service       |
     +------------------+      +------------------+
```

The backend also includes a background scheduler that periodically processes monitoring tasks and pending notification deliveries.

---

## Prerequisites

Before installing WatchTower, make sure the following software is installed on your system.

| Requirement | Purpose |
|---|---|
| Python | Backend runtime |
| PostgreSQL | Database |
| Git | Repository management |
| pip | Python dependency installation |
| Modern web browser | Accessing the application |

You will also need:

- An active internet connection for website monitoring.
- PostgreSQL running locally or an accessible PostgreSQL instance.
- SMTP credentials if you want to enable email notifications.
- VAPID keys if you want to configure browser push notifications.

The instructions below describe local development setup.

---

## Installation and Setup

Follow these steps to download and run WatchTower on your local machine.

### 1. Clone the Repository

Open a terminal or command prompt and execute:

```bash
git clone https://github.com/PrashantsGit/WatchTower.git
```

Navigate to the project directory:

```bash
cd WatchTower
```

Alternatively, download the repository as a ZIP file:

1. Open the [WatchTower GitHub Repository](https://github.com/PrashantsGit/WatchTower).
2. Click the **Code** button.
3. Select **Download ZIP**.
4. Extract the downloaded ZIP file.
5. Open a terminal inside the extracted `WatchTower` directory.

### 2. Create a Virtual Environment

It is recommended to use a Python virtual environment to keep project dependencies isolated.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell prevents script execution, run the following command in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project's Python dependencies:

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browser

If Playwright is part of the installed project dependencies, install its Chromium browser binary:

```bash
playwright install chromium
```

On supported Linux environments, if browser system dependencies are missing, you may also need:

```bash
playwright install-deps chromium
```

### 5. Configure PostgreSQL

WatchTower uses PostgreSQL for persistent data storage.

1. Download and install PostgreSQL from [postgresql.org/download](https://www.postgresql.org/download/).
2. Make sure the PostgreSQL service is running.
3. Create a database named `watchtower`.

Using `psql`, execute:

```sql
CREATE DATABASE watchtower;
```

You can also create the database through pgAdmin.

Remember the PostgreSQL username and password because they will be required in the application configuration.

### 6. Configure Environment Variables

Create a local `.env` file in the project root by copying `.env.example`.

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Windows (Command Prompt):**

```cmd
copy .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Open `.env` and configure the required values. For example:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/watchtower
SECRET_KEY=YOUR_SECRET_KEY
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

Generate a secure secret key using Python:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated value into `SECRET_KEY`.

**Important:**
- Use your actual PostgreSQL credentials.
- Do not use an example secret key in a real environment.
- Keep your `.env` file private.
- Never commit `.env` or real credentials to GitHub.
- Check `.env.example` for the exact configuration keys supported by the current repository version. Retain and configure any additional required variables.

**Optional integrations:** Configure the SMTP settings in `.env.example` if you want to use email notifications. Configure the VAPID settings if you want to use browser push notifications. These integrations require valid credentials and provider configuration.

### 7. Run Database Migrations

Once PostgreSQL and environment variables are configured, initialize the database schema using Alembic.

From the project root, run:

```bash
alembic upgrade head
```

This applies the available database migrations.

### 8. Start the Backend

Make sure your virtual environment is activated.

From the project root, run:

```bash
uvicorn main:app --reload
```

The FastAPI backend should start at:

```text
http://127.0.0.1:8000
```

Keep this terminal running while using the application.

### 9. Start the Frontend

Open a **second terminal** in the project directory.

Start the frontend using Python's built-in HTTP server:

```bash
python -m http.server 5500 --directory frontend
```

The frontend will be available at:

```text
http://127.0.0.1:5500
```

Keep both terminals running:

- Terminal 1: FastAPI backend.
- Terminal 2: Frontend development server.

---

## Accessing the Application

Once both servers are running, use the following URLs:

| Service | URL |
|---|---|
| WatchTower Frontend | http://127.0.0.1:5500 |
| Backend API | http://127.0.0.1:8000 |
| Interactive API Documentation | http://127.0.0.1:8000/docs |
| OpenAPI Schema | http://127.0.0.1:8000/openapi.json |

Open the frontend in your browser and register an account to get started.

**Note:** The frontend must be able to communicate with the backend API. If you use a different backend host or port, ensure the frontend API configuration and backend CORS settings match your environment.

---

## API Overview

WatchTower exposes RESTful API endpoints under the `/api` prefix.

| Module | Endpoint | Description |
|---|---|---|
| Authentication | `/api/auth/register` | Register a new user |
| Authentication | `/api/auth/login` | Authenticate a user |
| Authentication | `/api/auth/logout` | Log out and revoke the token |
| Authentication | `/api/auth/me` | Retrieve authenticated user details |
| Tasks | `/api/tasks` | Create and retrieve monitoring tasks |
| Tasks | `/api/tasks/{task_id}` | Retrieve, update, or delete a task |
| Tasks | `/api/tasks/{task_id}/pause` | Pause a monitoring task |
| Tasks | `/api/tasks/{task_id}/resume` | Resume a monitoring task |
| Rules | `/api/tasks/{task_id}/rules` | Manage monitoring rules |
| History | `/api/history` | Retrieve monitoring history |
| History | `/api/tasks/{task_id}/history` | Retrieve task-specific history |
| Notifications | `/api/notifications` | Manage notifications |
| Dashboard | `/api/dashboard` | Retrieve dashboard information |
| User | `/api/users/me` | Manage user profile information |

For detailed request parameters, response formats, validation rules, and authentication requirements, refer to the API Specification in the `docs` directory.

---

## Monitoring Workflow

A typical WatchTower monitoring cycle follows this process:

1. A user registers and logs in.
2. The user creates a website monitoring task.
3. The user configures monitoring rules.
4. The background scheduler identifies tasks that are due for monitoring.
5. The monitoring engine retrieves and extracts website information.
6. Extracted information is evaluated against configured rules.
7. Meaningful changes are recorded as monitoring events.
8. Notifications are generated and processed according to user preferences.
9. The user reviews monitoring activity and notifications through the dashboard.

---

## Project Structure

The project is organized into separate modules to maintain separation of concerns and make development easier.

```text
WatchTower/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── monitoring/
│   ├── scheduler/
│   └── notifications/
├── alembic/
│   └── versions/
├── docs/
├── frontend/
├── tests/
│   ├── unit/
│   └── integration/
├── .env.example
├── .gitignore
├── alembic.ini
├── main.py
├── requirements.txt
└── README.md
```

---

## Running Tests

WatchTower uses Pytest for automated testing.

Before running the tests, ensure that:

- Your virtual environment is activated.
- Project dependencies are installed.
- PostgreSQL is running.
- Required environment variables are configured.
- The test database configuration is correct.

Run the complete test suite:

```bash
pytest -v
```

Run unit tests:

```bash
pytest tests/unit -v
```

Run integration tests:

```bash
pytest tests/integration -v
```

---

## Configuration Reference

The following are examples of configuration settings used by the application. The exact supported variables are defined in `.env.example`.

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL database connection string |
| `SECRET_KEY` | Secret used for application authentication |
| SMTP settings | Configuration for email delivery |
| VAPID settings | Configuration for browser push notifications |

Always refer to `.env.example` for the exact configuration keys supported by the current repository version.

---

## Troubleshooting

### Python is not recognized

Make sure Python is installed and added to your system PATH.

Verify installation:

```bash
python --version
```

On some Linux/macOS systems, use:

```bash
python3 --version
```

### pip is not recognized

Use:

```bash
python -m pip install -r requirements.txt
```

### Virtual environment activation is blocked on Windows

In PowerShell, execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### PostgreSQL connection error

Check the following:

- PostgreSQL service is running.
- The database named `watchtower` exists.
- Database username and password are correct.
- `DATABASE_URL` in `.env` is correct.
- PostgreSQL is accessible on the configured host and port.

### Missing environment variables

Make sure `.env` exists in the project root and contains the required variables. Check `.env.example` for the expected configuration keys.

### Playwright browser error

Install the Chromium browser binary:

```bash
playwright install chromium
```

### Database migration error

Ensure PostgreSQL is running and the database connection string is valid.

Then retry:

```bash
alembic upgrade head
```

### Frontend cannot connect to backend

Verify that:

- The FastAPI backend is running.
- The backend is accessible at `http://127.0.0.1:8000`.
- The frontend API base URL points to the correct backend.
- Backend CORS configuration allows the frontend's origin.

---

## Security Notes

Security is an important consideration when deploying or developing WatchTower.

The application includes authentication and access-control mechanisms such as:

- JWT-based authentication.
- Password hashing.
- Token revocation during logout.
- User-level resource isolation.
- Environment-based configuration for sensitive values.

For deployments beyond local development, review:

- HTTPS configuration.
- CORS restrictions.
- Secret and credential management.
- Database access permissions.
- Authentication and authorization.
- Rate limiting.
- Logging and error handling.

Never publish database passwords, authentication secrets, SMTP credentials, VAPID private keys, or other sensitive information.

---

## Documentation

Technical documentation is available in the `docs/` directory.

| Document | Description |
|---|---|
| Software Requirements Specification | Defines project scope, requirements, and expected functionality. |
| Software Architecture Design | Describes architectural components, layers, and interactions. |
| Database Design | Documents database entities, relationships, and schema design. |
| Development Guidelines | Defines coding conventions and development practices. |
| API Specification | Documents API endpoints, request structures, and responses. |

---

## Future Enhancements

Potential areas for future development include:

- Improved responsive frontend experience.
- Additional monitoring and extraction strategies.
- More configurable monitoring intervals.
- Advanced monitoring analytics and reporting.
- Additional notification channels.
- Improved monitoring scalability.
- Containerized deployment using Docker.
- Automated CI/CD workflows.

---

## Contributing

Contributions, suggestions, and bug reports are welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a new feature branch.
3. Implement your changes.
4. Test your changes.
5. Submit a pull request with a clear description.

For significant changes, consider opening an issue first to discuss the proposed implementation.

Please follow the existing project structure and development guidelines when contributing.

---

## License

No open-source license has been selected for this repository yet.

Until a license is added, making the repository public does not automatically grant permission to use, modify, or distribute its code.

---

<p align="center">
  <strong>WatchTower — Monitor. Detect. Notify.</strong>
</p>
