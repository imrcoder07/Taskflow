from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Project
from app.forms import ProjectForm

projects = Blueprint("projects", __name__, url_prefix="/projects")


@projects.route("/")
@login_required
def index():
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("projects/list.html", projects=all_projects)


@projects.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if not current_user.is_admin:
        flash("You do not have permission to create projects.", "danger")
        return redirect(url_for("projects.index"))

    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data.strip(),
            description=form.description.data.strip(),
            created_by=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash("Project created successfully!", "success")
        return redirect(url_for("projects.index"))

    return render_template("projects/create.html", form=form)


@projects.route("/<int:project_id>")
@login_required
def view(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        abort(404)
    # Tasks will be implemented in Phase 5
    return render_template("projects/view.html", project=project)
