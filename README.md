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
- **Dynamic Dashboard:**
  - Real-time aggregated statistics showing total tasks, pending tasks, completed tasks, and overdue tasks.
  - Segmented data visibility: Admins see system-wide stats, while members see metrics tailored strictly to their assigned tasks.
- **Modern UI:**
  - Premium, production-level SaaS interface featuring a refined **Dark + Rose** color theme.
  - Responsive grid layouts, strict typography hierarchy, and subtle interaction depth (hover states, custom badges, and soft shadows) built cleanly with Tailwind CSS.

## 💻 Tech Stack

- **Backend:** Python 3, Flask 3.1, SQLAlchemy 2.0 (via Flask-SQLAlchemy)
- **Database:** PostgreSQL (production ready via `psycopg2-binary`), SQLite (for local development/testing)
- **Frontend:** HTML5, Jinja2, Tailwind CSS (CDN)
- **Testing:** Pytest, Pytest-Flask
- **Server:** Gunicorn (production WSGI server)

## 🛠 Setup & Installation

### Prerequisites
- Python 3.10+
- (Optional) PostgreSQL database if deploying to production.

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
   # DATABASE_URL=postgresql://user:password@localhost/taskflow (Optional for local, uses SQLite by default)
   ```

5. **Initialize the Database & Create Admin:**
   Running the app for the first time will automatically create the SQLite database and provision a default administrator account.
   ```bash
   python run.py
   ```
   **Default Admin Credentials:**
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
