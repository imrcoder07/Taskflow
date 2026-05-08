import os
from app import create_app, db

# FLASK_ENV is deprecated in Flask 3.x; use APP_ENV to select config profile
config_name = os.environ.get("APP_ENV", "development")
app = create_app(config_name)


with app.app_context():
    db.create_all()


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "app": app}


if __name__ == "__main__":
    app.run(
        debug=app.config.get("DEBUG", False),
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
    )
