from datetime import date, datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user

from app import db
from app.models import Project, Task, User

api = Blueprint("api", __name__, url_prefix="/api")


@api.before_request
def require_api_login():
    if not current_user.is_authenticated:
        return error_response("Authentication required.", 401)


def error_response(message, status_code=400, errors=None):
    payload = {"error": message}
    if errors:
        payload["errors"] = errors
    return jsonify(payload), status_code


def get_json_payload():
    payload = request.get_json(silent=True)
    if payload is None:
        return None, error_response("Request body must be valid JSON.", 400)
    return payload, None


def parse_due_date(value, errors):
    if value in (None, ""):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        errors["due_date"] = "Use YYYY-MM-DD format."
        return None


def project_to_dict(project, include_tasks=False):
    data = {
        "id": project.id,
        "name": project.name,
        "description": project.description or "",
        "created_by": project.created_by,
        "created_at": project.created_at.isoformat() if project.created_at else None,
    }
    if include_tasks:
        data["tasks"] = [task_to_dict(task) for task in project.tasks.order_by(Task.created_at.desc()).all()]
    return data


def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description or "",
        "status": task.status,
        "due_date": task.due_date.isoformat() if isinstance(task.due_date, date) else None,
        "project_id": task.project_id,
        "assigned_to": task.assigned_to,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }


def validate_project_payload(payload, partial=False):
    errors = {}
    cleaned = {}

    if not partial or "name" in payload:
        name = (payload.get("name") or "").strip()
        if not name:
            errors["name"] = "Project name is required."
        elif len(name) > 200:
            errors["name"] = "Project name must be 200 characters or fewer."
        else:
            cleaned["name"] = name

    if "description" in payload:
        description = (payload.get("description") or "").strip()
        if len(description) > 2000:
            errors["description"] = "Description must be 2000 characters or fewer."
        else:
            cleaned["description"] = description
    elif not partial:
        cleaned["description"] = ""

    return cleaned, errors


def validate_task_payload(payload, partial=False):
    errors = {}
    cleaned = {}

    if not partial or "title" in payload:
        title = (payload.get("title") or "").strip()
        if not title:
            errors["title"] = "Task title is required."
        elif len(title) > 200:
            errors["title"] = "Task title must be 200 characters or fewer."
        else:
            cleaned["title"] = title

    if "description" in payload:
        description = (payload.get("description") or "").strip()
        if len(description) > 2000:
            errors["description"] = "Description must be 2000 characters or fewer."
        else:
            cleaned["description"] = description
    elif not partial:
        cleaned["description"] = ""

    if not partial or "status" in payload:
        status = payload.get("status", "pending")
        if status not in Task.VALID_STATUSES:
            errors["status"] = "Status must be pending, in_progress, or done."
        else:
            cleaned["status"] = status

    if not partial or "project_id" in payload:
        project_id = payload.get("project_id")
        project = db.session.get(Project, project_id) if isinstance(project_id, int) else None
        if not project:
            errors["project_id"] = "Choose an existing project."
        else:
            cleaned["project_id"] = project_id

    if "assigned_to" in payload:
        assigned_to = payload.get("assigned_to")
        if assigned_to in (None, 0, ""):
            cleaned["assigned_to"] = None
        elif isinstance(assigned_to, int) and db.session.get(User, assigned_to):
            cleaned["assigned_to"] = assigned_to
        else:
            errors["assigned_to"] = "Choose an existing user or leave the task unassigned."
    elif not partial:
        cleaned["assigned_to"] = None

    if "due_date" in payload:
        cleaned["due_date"] = parse_due_date(payload.get("due_date"), errors)
    elif not partial:
        cleaned["due_date"] = None

    return cleaned, errors


@api.get("/projects")
def list_projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return jsonify({"projects": [project_to_dict(project) for project in projects]})


@api.post("/projects")
def create_project():
    if not current_user.is_admin:
        return error_response("Admin access required.", 403)

    payload, error = get_json_payload()
    if error:
        return error

    cleaned, errors = validate_project_payload(payload)
    if errors:
        return error_response("Validation failed.", 400, errors)

    project = Project(created_by=current_user.id, **cleaned)
    db.session.add(project)
    db.session.commit()
    return jsonify({"project": project_to_dict(project)}), 201


@api.get("/projects/<int:project_id>")
def get_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        return error_response("Project not found.", 404)
    return jsonify({"project": project_to_dict(project, include_tasks=True)})


@api.put("/projects/<int:project_id>")
def update_project(project_id):
    if not current_user.is_admin:
        return error_response("Admin access required.", 403)

    project = db.session.get(Project, project_id)
    if not project:
        return error_response("Project not found.", 404)

    payload, error = get_json_payload()
    if error:
        return error

    cleaned, errors = validate_project_payload(payload, partial=True)
    if errors:
        return error_response("Validation failed.", 400, errors)

    for field, value in cleaned.items():
        setattr(project, field, value)
    db.session.commit()
    return jsonify({"project": project_to_dict(project)})


@api.delete("/projects/<int:project_id>")
def delete_project(project_id):
    if not current_user.is_admin:
        return error_response("Admin access required.", 403)

    project = db.session.get(Project, project_id)
    if not project:
        return error_response("Project not found.", 404)

    db.session.delete(project)
    db.session.commit()
    return "", 204


@api.get("/tasks")
def list_tasks():
    if current_user.is_admin:
        query = Task.query
    else:
        query = Task.query.filter_by(assigned_to=current_user.id)
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify({"tasks": [task_to_dict(task) for task in tasks]})


@api.post("/tasks")
def create_task():
    if not current_user.is_admin:
        return error_response("Admin access required.", 403)

    payload, error = get_json_payload()
    if error:
        return error

    cleaned, errors = validate_task_payload(payload)
    if errors:
        return error_response("Validation failed.", 400, errors)

    task = Task(**cleaned)
    db.session.add(task)
    db.session.commit()
    return jsonify({"task": task_to_dict(task)}), 201


@api.get("/tasks/<int:task_id>")
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return error_response("Task not found.", 404)
    if not current_user.is_admin and task.assigned_to != current_user.id:
        return error_response("You can only view tasks assigned to you.", 403)
    return jsonify({"task": task_to_dict(task)})


@api.put("/tasks/<int:task_id>")
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return error_response("Task not found.", 404)

    if not current_user.is_admin and task.assigned_to != current_user.id:
        return error_response("You can only update tasks assigned to you.", 403)

    payload, error = get_json_payload()
    if error:
        return error

    if current_user.is_admin:
        cleaned, errors = validate_task_payload(payload, partial=True)
    else:
        extra_fields = set(payload) - {"status"}
        cleaned, errors = {}, {}
        if extra_fields:
            errors["fields"] = "Members can only update task status."
        status = payload.get("status")
        if status not in Task.VALID_STATUSES:
            errors["status"] = "Status must be pending, in_progress, or done."
        else:
            cleaned["status"] = status

    if errors:
        return error_response("Validation failed.", 400, errors)

    for field, value in cleaned.items():
        setattr(task, field, value)
    db.session.commit()
    return jsonify({"task": task_to_dict(task)})


@api.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    if not current_user.is_admin:
        return error_response("Admin access required.", 403)

    task = db.session.get(Task, task_id)
    if not task:
        return error_response("Task not found.", 404)

    db.session.delete(task)
    db.session.commit()
    return "", 204
