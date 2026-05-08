import pytest

from app import db
from app.models import Project, Task, User


def test_invalid_user_role_is_rejected(app):
    with pytest.raises(ValueError):
        User(name="Bad Role", email="bad-role@test.com", role="owner")


def test_invalid_task_status_is_rejected(project):
    with pytest.raises(ValueError):
        Task(title="Bad Status", status="blocked", project_id=project.id)


def test_task_requires_existing_project(client, admin_user, member_user):
    client.post("/auth/login", data={"email": admin_user.email, "password": "Admin123!"})

    response = client.post("/tasks/new", data={
        "title": "Invalid Project Task",
        "description": "This should not save.",
        "status": "pending",
        "due_date": "2026-12-31",
        "project_id": 99999,
        "assigned_to": member_user.id,
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Not a valid choice." in response.data or b"Choose an existing project." in response.data
    assert Task.query.filter_by(title="Invalid Project Task").first() is None


def test_task_requires_existing_assignee(client, admin_user, project):
    client.post("/auth/login", data={"email": admin_user.email, "password": "Admin123!"})

    response = client.post("/tasks/new", data={
        "title": "Invalid Assignee Task",
        "description": "This should not save.",
        "status": "pending",
        "due_date": "2026-12-31",
        "project_id": project.id,
        "assigned_to": 99999,
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Not a valid choice." in response.data or b"Choose an existing user" in response.data
    assert Task.query.filter_by(title="Invalid Assignee Task").first() is None


def test_deleting_project_deletes_related_tasks(app, project):
    with app.app_context():
        project_id = project.id
        task = Task(title="Cascade Task", status="pending", project_id=project_id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        db.session.delete(db.session.get(Project, project_id))
        db.session.commit()

        assert db.session.get(Task, task_id) is None
