# TaskFlow

> A role-based task and project management system built with Flask, PostgreSQL, and a modern SaaS-inspired interface.

TaskFlow is a full-stack web application that enables structured team collaboration through clearly defined admin and member workflows, granular access control, and a REST API alongside a server-rendered UI.

---

## 🌐 Live Demo

[**TaskFlow — Live Application**](https://taskflow-mu6q.onrender.com/)

**Admin Credentials (for testing):**
- **Email:** `admin@taskflow.com`
- **Password:** `Admin123!`

> _Deployed on Render with a managed PostgreSQL database._

---

## 📸 Screenshots

| Homepage | Dashboard | Task Management |
|----------|-----------|-----------------|
| ![Homepage](screenshots/homepage.png) | ![Dashboard](screenshots/dashboard.png) | ![Tasks](screenshots/tasks.png) |


---

## ✨ Features

### Role-Based Access Control (RBAC)
- **Admins** have full CRUD access over projects, tasks, and user assignments.
- **Members** can view their assigned tasks and update task status — nothing more.
- Role enforcement is applied at both the UI layer and the REST API layer.

### Authentication & Security
- Session-based authentication via `Flask-Login`.
- Passwords hashed using `werkzeug.security` (PBKDF2-SHA256).
- Global CSRF protection on all forms via `Flask-WTF`.
- Open redirect protection on post-login redirects.

### Project & Task Management
- Create and manage projects with associated task lists.
- Track tasks through three statuses: `Pending`, `In Progress`, and `Done`.
- Assign tasks to specific team members with optional due dates.
- Backend guards prevent tasks from being created with past due dates.
- Unassigned tasks cannot be marked as completed.

### REST API
- JSON endpoints under `/api` for full project and task management.
- Respects the same session authentication and RBAC rules as the web UI.
- Includes backend validation for task relationships and workflow state transitions.

### Dashboard Analytics
- Aggregated statistics: total, pending, completed, and overdue tasks.
- Admins see system-wide metrics; members see a personal workload view.

### UI & Interaction Design
- Modern SaaS-inspired interface with a cohesive dark theme and subtle accent colors.
- Responsive layouts designed for both desktop and tablet viewports.
- Muted status badges, soft card borders, and polished hover states for a clean visual hierarchy.
- Flash notifications auto-dismiss with a smooth fade-out transition.

---

## 🏗 Architecture

```
TaskFlow
├── Flask (application server)          # Routing, auth, business logic
│   ├── Jinja2                          # Server-side HTML rendering
│   └── REST API (/api)                 # JSON endpoints for programmatic access
├── SQLAlchemy 2.0                      # ORM for relational data modeling
├── PostgreSQL                          # Primary datastore (production & development)
│   └── SQLite (fallback)              # Used automatically when DATABASE_URL is unset
└── Gunicorn                            # WSGI server for production deployment
```

The application uses a traditional server-rendered architecture (Flask + Jinja2) with REST API endpoints layered in for extensibility. All business logic, access control, and validation live in the backend — the API and UI share the same rules. SQLAlchemy handles relational integrity including cascaded deletes and role-level check constraints at the database level.

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.10+ |
| **Web Framework** | Flask 3.1 |
| **ORM** | SQLAlchemy 2.0 via Flask-SQLAlchemy |
| **Database** | PostgreSQL (production), SQLite (local fallback) |
| **Templating** | Jinja2 |
| **Frontend** | HTML5, Tailwind CSS (CDN) |
| **Auth** | Flask-Login, Flask-WTF |
| **Testing** | Pytest, Pytest-Flask |
| **Server** | Gunicorn |
| **Deployment** | Render |

---

## 🔌 REST API Reference

Authenticate via `/auth/login` first (session cookie is shared), then call the JSON endpoints.

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/projects` | All | List all projects |
| `POST` | `/api/projects` | Admin | Create a new project |
| `GET` | `/api/projects/<id>` | All | Get a project with its tasks |
| `PUT` | `/api/projects/<id>` | Admin | Update a project |
| `DELETE` | `/api/projects/<id>` | Admin | Delete a project |
| `GET` | `/api/tasks` | All | List tasks (all for admin, assigned for member) |
| `POST` | `/api/tasks` | Admin | Create a task |
| `GET` | `/api/tasks/<id>` | All | Get a single task |
| `PUT` | `/api/tasks/<id>` | All | Update task (members: status only) |
| `DELETE` | `/api/tasks/<id>` | Admin | Delete a task |

**Example — Create a task via cURL:**

```bash
curl -X POST https://taskflow-mu6q.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement login flow",
    "status": "pending",
    "project_id": 1,
    "assigned_to": 2
  }'
```

---

## ⚙️ Local Setup

### Prerequisites

- Python 3.10+
- PostgreSQL (or use the SQLite fallback for quick local testing)

### Installation

**1. Clone the repository:**
```bash
git clone <repository_url>
cd TaskFlow
```

**2. Create and activate a virtual environment:**
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables:**

Copy the example file and fill in your values:
```bash
cp .env.example .env
```

`.env` reference:
```env
APP_ENV=development
SECRET_KEY=your-super-secret-development-key
DATABASE_URL=postgresql://user:password@localhost/taskflow

# Admin bootstrap — creates or promotes the admin account on startup
ADMIN_NAME=TaskFlow Admin
ADMIN_EMAIL=admin@taskflow.com
ADMIN_PASSWORD=Admin123!
ADMIN_RESET_PASSWORD=false
```

> If `DATABASE_URL` is not set, the app automatically falls back to a local SQLite database.

**5. Run the application:**
```bash
python run.py
```

The database tables are created automatically on first run. The admin account is created or promoted on startup if `ADMIN_EMAIL` and `ADMIN_PASSWORD` are set. To reset an existing admin's password, set `ADMIN_RESET_PASSWORD=true`, restart once, then revert to `false`.

**6. Run the test suite:**
```bash
python -m pytest -v
```

---

## 🚀 Deployment (Render)

**1. Connect your GitHub repository** to Render and create a new Web Service.

**2. Configure the start command:**
```bash
gunicorn run:app
```

**3. Set the following environment variables** in the Render dashboard:

```env
APP_ENV=production
SECRET_KEY=<generate-a-secure-random-string>
DATABASE_URL=<your-managed-postgresql-connection-string>
ADMIN_NAME=TaskFlow Admin
ADMIN_EMAIL=admin@taskflow.com
ADMIN_PASSWORD=<secure-admin-password>
ADMIN_RESET_PASSWORD=false
```

**4. Provision a PostgreSQL database** through Render (or any managed provider) and copy the external connection URL into `DATABASE_URL`.

> After changing admin-related environment variables, trigger a manual redeploy so the bootstrap logic runs against the production database.

A `Procfile` is included in the repository root for platforms that use it.

---

## 📁 Project Structure

```
TaskFlow/
├── app/
│   ├── routes/          # Blueprints: auth, dashboard, projects, tasks, api
│   ├── templates/       # Jinja2 HTML templates
│   ├── models.py        # SQLAlchemy models: User, Project, Task
│   └── __init__.py      # App factory and extension initialization
├── tests/               # Pytest test suite
├── config.py            # Environment-based configuration
├── run.py               # Application entrypoint with DB init and admin bootstrap
├── Procfile             # Gunicorn start command for PaaS deployment
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variable reference
```

---

## 🧪 Testing

The test suite covers authentication, RBAC enforcement, task workflow rules, and API endpoint behavior.

```bash
# Run all tests with verbose output
python -m pytest -v

# Run a specific test file
python -m pytest tests/test_api.py -v
```

---

## 📄 License

This project is intended for portfolio and evaluation purposes.

---

_Built with Flask and PostgreSQL._
