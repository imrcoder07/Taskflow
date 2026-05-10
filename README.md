# TaskFlow

TaskFlow is a role-based task and project management system built with Flask and PostgreSQL. It allows teams to organize their work efficiently, providing administrative controls for project and task management while giving members a streamlined interface to update their task progress. 

## 🚀 Features

- **Role-Based Access Control (RBAC):**
  - **Admins:** Full CRUD capabilities for Projects and Tasks. Can assign tasks to members.
  - **Members:** Can view their assigned tasks and update task statuses. Restricted from modifying core project or task metadata.
- **Authentication & Security:**
  - Secure session-based authentication using `Flask-Login`.
  - Passwords hashed using `werkzeug.security`.
  - Hardened endpoints with protection against open redirects (CWE-601).
  - Global CSRF protection with `Flask-WTF`.
- **Project & Task Management:**
  - Create and manage distinct projects.
  - Create tasks within projects, assign due dates, and track statuses (`Pending`, `In Progress`, `Done`).
- **REST API:**
  - JSON endpoints under `/api` for project and task CRUD operations.
  - Uses the existing Flask session authentication and role-based permissions.
  - Admins can create, update, and delete projects/tasks; members can view assigned tasks and update task status.
- **Dynamic Dashboard:**
  - Real-time aggregated statistics showing total tasks, pending tasks, completed tasks, and overdue tasks.
  - Segmented data visibility: Admins see system-wide stats, while members see metrics tailored strictly to their assigned tasks.
- **Modern UI:**
  - Premium, production-level SaaS interface featuring a refined **Dark + Rose** color theme.
  - Responsive grid layouts, strict typography hierarchy, and subtle interaction depth (hover states, custom badges, and soft shadows) built cleanly with Tailwind CSS.

## 💻 Tech Stack

- **Backend:** Python 3, Flask 3.1, SQLAlchemy 2.0 (via Flask-SQLAlchemy)
- **Database:** PostgreSQL for development and production via `psycopg2-binary`; SQLite is retained as a fallback/testing database.
- **Frontend:** HTML5, Jinja2, Tailwind CSS (CDN)
- **Testing:** Pytest, Pytest-Flask
- **Server:** Gunicorn (production WSGI server)

## 🛠 Setup & Installation

## REST API

The app includes REST API routes alongside the existing Jinja pages. Log in through the normal `/auth/login` page first, then call the JSON endpoints using the same session.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/projects` | List projects |
| `POST` | `/api/projects` | Create a project, admin only |
| `GET` | `/api/projects/<id>` | Get one project with tasks |
| `PUT` | `/api/projects/<id>` | Update a project, admin only |
| `DELETE` | `/api/projects/<id>` | Delete a project, admin only |
| `GET` | `/api/tasks` | List all tasks for admins, assigned tasks for members |
| `POST` | `/api/tasks` | Create a task, admin only |
| `GET` | `/api/tasks/<id>` | Get one task |
| `PUT` | `/api/tasks/<id>` | Update a task; members can update status only |
| `DELETE` | `/api/tasks/<id>` | Delete a task, admin only |

Example JSON request:

```bash
curl -X POST https://your-app.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"API Task","status":"pending","project_id":1,"assigned_to":2}'
```

### Prerequisites
- Python 3.10+
- PostgreSQL database for development/production.

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd TaskFlow
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```env
   APP_ENV=development
   SECRET_KEY=your-super-secret-development-key
   DATABASE_URL=postgresql://user:password@localhost/taskflow
   ```

5. **Initialize the Database:**
   Running the app for the first time will automatically create the required tables in the configured PostgreSQL database. If `DATABASE_URL` is not set, the app falls back to a local SQLite database.
   ```bash
   python run.py
   ```
   **Admin Credentials:**
   Set these environment variables before deployment to create an admin account automatically. This does not add any public UI for creating admin accounts.
   ```env
   ADMIN_NAME=TaskFlow Admin
   ADMIN_EMAIL=admin@taskflow.com
   ADMIN_PASSWORD=Admin123!
   ADMIN_RESET_PASSWORD=false
   ```
   If the email already exists, the app keeps the existing password and only upgrades the user role to admin. To reset the password for an existing admin, temporarily set `ADMIN_RESET_PASSWORD=true`, deploy once, then change it back to `false`.

   Local development example:
   - **Email:** `admin@taskflow.com`
   - **Password:** `Admin123!`

6. **Run Tests:**
   Ensure the application is stable by running the comprehensive test suite:
   ```bash
   python -m pytest -v
   ```

## 🚀 Deployment

The application is fully prepared for deployment on platforms like Render or Railway. A `Procfile` is included.

1. Connect your GitHub repository to your preferred hosting provider.
2. Set the start command or let the provider use the `Procfile`:
   ```bash
   gunicorn run:app
   ```
3. **Environment Variables Required in Production:**
   - `APP_ENV=production`
   - `SECRET_KEY=<generate-a-secure-random-string>`
   - `DATABASE_URL=<your-managed-postgresql-url>`

---
*Built with Flask, crafted with Tailwind.*
