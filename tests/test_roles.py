from app.models import Task
from app import db

def test_member_cannot_create_project(client, member_user):
    client.post('/auth/login', data={'email': member_user.email, 'password': 'Member123!'})
    response = client.get('/projects/new', follow_redirects=True)
    assert b'You do not have permission to create projects.' in response.data

def test_member_cannot_create_task(client, member_user):
    client.post('/auth/login', data={'email': member_user.email, 'password': 'Member123!'})
    response = client.get('/tasks/new', follow_redirects=True)
    assert b'You do not have permission to create tasks.' in response.data

def test_member_can_update_own_task_status(client, member_user, project, app):
    with app.app_context():
        # Create a task assigned to member
        task = Task(title='Member Task', description='Desc', status='pending', project_id=project.id, assigned_to=member_user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    
    client.post('/auth/login', data={'email': member_user.email, 'password': 'Member123!'})
    response = client.post(f'/tasks/{task_id}/edit', data={
        'status': 'in_progress'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Task status updated successfully!' in response.data
    
    with app.app_context():
        updated_task = db.session.get(Task, task_id)
        assert updated_task.status == 'in_progress'

def test_member_cannot_edit_task_metadata(client, member_user, project, app):
    with app.app_context():
        task = Task(title='Metadata Task', description='Desc', status='pending', project_id=project.id, assigned_to=member_user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
        
    client.post('/auth/login', data={'email': member_user.email, 'password': 'Member123!'})
    response = client.post(f'/tasks/{task_id}/edit', data={
        'title': 'Hacked Title',
        'status': 'done'
    }, follow_redirects=True)
    
    # Since member cannot edit metadata, they should either get a 403 or redirect with error, but looking at edit route:
    # `if current_user.is_admin:` ... handles form. Otherwise it just renders (for get) or skips? 
    # Let's check edit route. Wait, the route says:
    # if current_user.is_admin: process form.
    # else: renders form.html, but doesn't process POST.
    # So the title won't change.
    
    with app.app_context():
        task = db.session.get(Task, task_id)
        assert task.title == 'Metadata Task'
