from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/dashboard")
@login_required
def dashboard():
    from app.models import Task
    from datetime import date
    
    # Calculate global stats (for admin) or just user's stats
    if current_user.is_admin:
        base_query = Task.query
    else:
        base_query = Task.query.filter_by(assigned_to=current_user.id)
        
    total_tasks = base_query.count()
    completed_tasks = base_query.filter_by(status="done").count()
    pending_tasks = base_query.filter(Task.status.in_(["pending", "in_progress"])).count()
    overdue_tasks = base_query.filter(Task.due_date < date.today(), Task.status != "done").count()
    
    # Recent tasks for the UI
    tasks = base_query.order_by(Task.created_at.desc()).limit(5).all()
    
    return render_template("dashboard.html", 
                           tasks=tasks,
                           now=date.today(),
                           stats={
                               "total": total_tasks,
                               "completed": completed_tasks,
                               "pending": pending_tasks,
                               "overdue": overdue_tasks
                           })
