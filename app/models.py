from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    VALID_ROLES = ("admin", "member")
    __table_args__ = (
        db.CheckConstraint("role IN ('admin', 'member')", name="ck_users_role_valid"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")  # admin | member
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    projects_created = db.relationship(
        "Project", backref="creator", lazy="dynamic", foreign_keys="Project.created_by"
    )
    tasks_assigned = db.relationship(
        "Task", backref="assignee", lazy="dynamic", foreign_keys="Task.assigned_to"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @db.validates("role")
    def validate_role(self, key, role):
        if role not in self.VALID_ROLES:
            raise ValueError("Invalid user role.")
        return role

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    tasks = db.relationship(
        "Task",
        backref="project",
        lazy="dynamic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Project {self.name}>"


class Task(db.Model):
    __tablename__ = "tasks"
    VALID_STATUSES = ("pending", "in_progress", "done")
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('pending', 'in_progress', 'done')",
            name="ck_tasks_status_valid",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending | in_progress | done
    due_date = db.Column(db.Date, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @db.validates("status")
    def validate_status(self, key, status):
        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid task status.")
        return status

    def __repr__(self):
        return f"<Task {self.title} [{self.status}]>"
