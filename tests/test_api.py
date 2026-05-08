from app import db
from app.models import Project, Task


def login(client, user, password):
    return client.post("/auth/login", data={"email": user.email, "password": password})


def test_api_requires_login(client):
    response = client.get("/api/projects")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required."


def test_admin_can_create_project_with_api(client, admin_user):
    login(client, admin_user, "Admin123!")

    response = client.post("/api/projects", json={
        "name": "API Project",
        "description": "Created through JSON",
    })

    data = response.get_json()
    assert response.status_code == 201
    assert data["project"]["name"] == "API Project"
    assert Project.query.filter_by(name="API Project").first() is not None


def test_member_cannot_create_project_with_api(client, member_user):
    login(client, member_user, "Member123!")

    response = client.post("/api/projects", json={"name": "Forbidden"})

    assert response.status_code == 403
    assert response.get_json()["error"] == "Admin access required."


def test_api_validates_project_payload(client, admin_user):
    login(client, admin_user, "Admin123!")

    response = client.post("/api/projects", json={"name": "   "})

    assert response.status_code == 400
    assert "name" in response.get_json()["errors"]


def test_admin_can_create_task_with_api(client, admin_user, project, member_user):
    login(client, admin_user, "Admin123!")

    response = client.post("/api/tasks", json={
        "title": "API Task",
        "description": "Created through JSON",
        "status": "pending",
        "due_date": "2026-12-31",
        "project_id": project.id,
        "assigned_to": member_user.id,
    })

    data = response.get_json()
    assert response.status_code == 201
    assert data["task"]["title"] == "API Task"
    assert data["task"]["assigned_to"] == member_user.id


def test_api_validates_task_relationships(client, admin_user):
    login(client, admin_user, "Admin123!")

    response = client.post("/api/tasks", json={
        "title": "Bad Task",
        "status": "pending",
        "project_id": 99999,
        "assigned_to": 99999,
    })

    errors = response.get_json()["errors"]
    assert response.status_code == 400
    assert "project_id" in errors
    assert "assigned_to" in errors
    assert Task.query.filter_by(title="Bad Task").first() is None


def test_member_only_sees_assigned_tasks(client, member_user, project, admin_user):
    assigned = Task(title="Assigned", status="pending", project_id=project.id, assigned_to=member_user.id)
    hidden = Task(title="Hidden", status="pending", project_id=project.id, assigned_to=admin_user.id)
    db.session.add_all([assigned, hidden])
    db.session.commit()

    login(client, member_user, "Member123!")
    response = client.get("/api/tasks")

    titles = {task["title"] for task in response.get_json()["tasks"]}
    assert response.status_code == 200
    assert titles == {"Assigned"}


def test_member_can_update_own_task_status_only(client, member_user, project):
    task = Task(title="Own API Task", status="pending", project_id=project.id, assigned_to=member_user.id)
    db.session.add(task)
    db.session.commit()

    login(client, member_user, "Member123!")
    response = client.put(f"/api/tasks/{task.id}", json={
        "title": "Changed Title",
        "status": "done",
    })

    assert response.status_code == 400
    assert "fields" in response.get_json()["errors"]
    assert db.session.get(Task, task.id).title == "Own API Task"

    response = client.put(f"/api/tasks/{task.id}", json={"status": "done"})

    assert response.status_code == 200
    assert response.get_json()["task"]["status"] == "done"


def test_admin_can_delete_task_with_api(client, admin_user, project):
    task = Task(title="Delete Me", status="pending", project_id=project.id)
    db.session.add(task)
    db.session.commit()
    task_id = task.id

    login(client, admin_user, "Admin123!")
    response = client.delete(f"/api/tasks/{task_id}")

    assert response.status_code == 204
    assert db.session.get(Task, task_id) is None
