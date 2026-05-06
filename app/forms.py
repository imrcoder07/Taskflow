from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User


class SignupForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Create Account")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower().strip()).first()
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


class TaskForm(FlaskForm):
    title = StringField("Task Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Length(max=2000)])
    status = SelectField("Status", choices=[("pending", "Pending"), ("in_progress", "In Progress"), ("done", "Done")], default="pending")
    due_date = DateField("Due Date", format='%Y-%m-%d', validators=[Optional()])
    project_id = SelectField("Project", coerce=int, validators=[DataRequired()])
    assigned_to = SelectField("Assign To", coerce=int)
    submit = SubmitField("Save Task")


class StatusUpdateForm(FlaskForm):
    status = SelectField("Status", choices=[("pending", "Pending"), ("in_progress", "In Progress"), ("done", "Done")])
    submit = SubmitField("Update Status")
