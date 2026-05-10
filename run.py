import os
from app import create_app, db
from app.models import User

# FLASK_ENV is deprecated in Flask 3.x; use APP_ENV to select config profile
config_name = os.environ.get("APP_ENV", "development")
app = create_app(config_name)


def create_admin_from_env():
    admin_email = os.environ.get("ADMIN_EMAIL", "").lower().strip()
    admin_password = os.environ.get("ADMIN_PASSWORD", "")
    admin_name = os.environ.get("ADMIN_NAME", "TaskFlow Admin").strip()
    should_reset_password = os.environ.get("ADMIN_RESET_PASSWORD", "").lower() == "true"

    if not admin_email or not admin_password:
        return

    existing_user = User.query.filter_by(email=admin_email).first()
    if existing_user:
        if existing_user.role != "admin":
            existing_user.role = "admin"
        if should_reset_password:
            existing_user.set_password(admin_password)
        if db.session.is_modified(existing_user):
            db.session.commit()
        return

    admin = User(name=admin_name or "TaskFlow Admin", email=admin_email, role="admin")
    admin.set_password(admin_password)
    db.session.add(admin)
    db.session.commit()


with app.app_context():
    db.create_all()
    create_admin_from_env()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "app": app}


if __name__ == "__main__":
    app.run(
        debug=app.config.get("DEBUG", False),
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
    )
