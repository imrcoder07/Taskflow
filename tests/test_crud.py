from app.models import Project, Task

def test_admin_create_project(client, admin_user):
    client.post('/auth/login', data={'email': admin_user.email, 'password': 'Admin123!'})
    response = client.post('/projects/new', data={
        'name': 'New Testing Project',
        'description': 'A new project created in tests'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'New Testing Project' in response.data
    
    project = Project.query.filter_by(name='New Testing Project').first()
    assert project is not None

def test_admin_create_task(client, admin_user, project, member_user):
    client.post('/auth/login', data={'email': admin_user.email, 'password': 'Admin123!'})
    response = client.post('/tasks/new', data={
        'title': 'New Task',
        'description': 'Task description',
        'status': 'pending',
        'due_date': '2026-12-31',
        'project_id': project.id,
        'assigned_to': member_user.id
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'New Task' in response.data
    
    task = Task.query.filter_by(title='New Task').first()
    assert task is not None
    assert task.assigned_to == member_user.id
