from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app import db
from app.models import Task, Project, User
from app.forms import TaskForm

tasks = Blueprint("tasks", __name__, url_prefix="/tasks")


def _populate_task_form_choices(form):
    form.project_id.choices = [(p.id, p.name) for p in Project.query.order_by(Project.name).all()]
    form.assigned_to.choices = [(0, "Unassigned")] + [(u.id, u.name) for u in User.query.order_by(User.name).all()]


@tasks.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if not current_user.is_admin:
        flash("You do not have permission to create tasks.", "danger")
        return redirect(url_for("main.dashboard"))

    form = TaskForm()
    _populate_task_form_choices(form)

    # Pre-select project if passed in query string
    if request.method == "GET" and request.args.get("project_id"):
        try:
            form.project_id.data = int(request.args.get("project_id"))
        except ValueError:
            pass

    if form.validate_on_submit():
        task = Task(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            status=form.status.data,
            due_date=form.due_date.data,
            project_id=form.project_id.data,
            assigned_to=form.assigned_to.data if form.assigned_to.data > 0 else None
        )
        db.session.add(task)
        db.session.commit()
        flash("Task created successfully!", "success")
        return redirect(url_for("projects.view", project_id=task.project_id))

    return render_template("tasks/form.html", form=form, title="Create Task")


@tasks.route("/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit(task_id):
    from app.forms import StatusUpdateForm
    
    task = db.session.get(Task, task_id)
    if not task:
        abort(404)

    # Role enforcement
    if not current_user.is_admin and task.assigned_to != current_user.id:
        flash("You can only update tasks assigned to you.", "danger")
        return redirect(url_for("projects.view", project_id=task.project_id))

    if current_user.is_admin:
        form = TaskForm(obj=task)
        _populate_task_form_choices(form)

        # Convert None to 0 for the unassigned choice
        if request.method == "GET" and task.assigned_to is None:
            form.assigned_to.data = 0
            
        if form.validate_on_submit():
            task.title = form.title.data.strip()
            task.description = form.description.data.strip()
            task.status = form.status.data
            task.due_date = form.due_date.data
            task.project_id = form.project_id.data
            task.assigned_to = form.assigned_to.data if form.assigned_to.data > 0 else None
            
            db.session.commit()
            flash("Task updated successfully!", "success")
            return redirect(url_for("projects.view", project_id=task.project_id))
    else:
        # Member role: only status update allowed
        form = StatusUpdateForm(obj=task)
        if form.validate_on_submit():
            task.status = form.status.data
            db.session.commit()
            flash("Task status updated successfully!", "success")
            return redirect(url_for("projects.view", project_id=task.project_id))

    return render_template("tasks/form.html", form=form, title="Edit Task", task=task)


@tasks.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def delete(task_id):
    if not current_user.is_admin:
        flash("You do not have permission to delete tasks.", "danger")
        return redirect(url_for("main.dashboard"))

    task = db.session.get(Task, task_id)
    if not task:
        abort(404)

    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully.", "info")
    return redirect(url_for("projects.view", project_id=project_id))
