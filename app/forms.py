from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, Regexp
from app import db
from app.models import Project, Task, User


def _stripped(value):
    return value.strip() if isinstance(value, str) else value


COMPLETED_STATUSES = {"done", "completed"}


class SignupForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters."),
        Regexp(r".*[A-Z].*", message="Password must include at least one uppercase letter."),
        Regexp(r".*[a-z].*", message="Password must include at least one lowercase letter."),
        Regexp(r".*\d.*", message="Password must include at least one number."),
    ])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Create Account")

    def validate_name(self, name):
        if not _stripped(name.data):
            raise ValidationError("Name cannot be blank.")
        name.data = name.data.strip()

    def validate_email(self, email):
        email.data = email.data.lower().strip()
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is already registered.")


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")


class ProjectForm(FlaskForm):
    name = StringField("Project Name", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Length(max=2000)])
    submit = SubmitField("Create Project")

    def validate_name(self, name):
        if not _stripped(name.data):
            raise ValidationError("Project name cannot be blank.")
        name.data = name.data.strip()

    def validate_description(self, description):
        description.data = _stripped(description.data) or ""


class TaskForm(FlaskForm):
    title = StringField("Task Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Length(max=2000)])
    status = SelectField("Status", choices=[("pending", "Pending"), ("in_progress", "In Progress"), ("done", "Done")], default="pending")
    due_date = DateField("Due Date", format='%Y-%m-%d', validators=[Optional()])
    project_id = SelectField("Project", coerce=int, validators=[DataRequired()])
    assigned_to = SelectField("Assign To", coerce=int)
    submit = SubmitField("Save Task")

    def __init__(self, *args, allow_past_due_date=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_past_due_date = allow_past_due_date

    def validate_title(self, title):
        if not _stripped(title.data):
            raise ValidationError("Task title cannot be blank.")
        title.data = title.data.strip()

    def validate_description(self, description):
        description.data = _stripped(description.data) or ""

    def validate_status(self, status):
        if status.data not in Task.VALID_STATUSES:
            raise ValidationError("Choose a valid task status.")

    def validate_due_date(self, due_date):
        if due_date.data and not self.allow_past_due_date and due_date.data < date.today():
            raise ValidationError("Due date cannot be earlier than today.")

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators=extra_validators)
        is_unassigned = not self.assigned_to.data

        if is_unassigned and self.status.data in COMPLETED_STATUSES:
            self.status.errors.append("Unassigned tasks cannot be marked as completed.")
            return False

        return is_valid

    def validate_project_id(self, project_id):
        if not db_get(Project, project_id.data):
            raise ValidationError("Choose an existing project.")

    def validate_assigned_to(self, assigned_to):
        if assigned_to.data and not db_get(User, assigned_to.data):
            raise ValidationError("Choose an existing user or leave the task unassigned.")


class StatusUpdateForm(FlaskForm):
    status = SelectField("Status", choices=[("pending", "Pending"), ("in_progress", "In Progress"), ("done", "Done")])
    submit = SubmitField("Update Status")

    def validate_status(self, status):
        if status.data not in Task.VALID_STATUSES:
            raise ValidationError("Choose a valid task status.")


def db_get(model, record_id):
    if not record_id:
        return None
    return db.session.get(model, record_id)
