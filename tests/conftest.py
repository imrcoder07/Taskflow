import pytest
from app import create_app, db
from app.models import User, Project, Task

@pytest.fixture
def app():
    app = create_app('testing')
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-key"
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_user(app):
    admin = User(name="Admin", email="admin@test.com", role="admin")
    admin.set_password("Admin123!")
    db.session.add(admin)
    db.session.commit()
    return admin

@pytest.fixture
def member_user(app):
    member = User(name="Member", email="member@test.com", role="member")
    member.set_password("Member123!")
    db.session.add(member)
    db.session.commit()
    return member

@pytest.fixture
def project(app, admin_user):
    p = Project(name="Test Project", description="Test Desc", created_by=admin_user.id)
    db.session.add(p)
    db.session.commit()
    return p
