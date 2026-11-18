import os
from flask import Flask
from .database import init_db

def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "local-development-key"),
        DATABASE=os.environ.get("DATABASE_PATH", "aceest_fitness.db"),
        ADMIN_USERNAME=os.environ.get("ADMIN_USERNAME", "admin"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD")
    )

    if test_config:
        app.config.update(test_config)

    init_db(
        app.config["DATABASE"],
        app.config["ADMIN_USERNAME"],
        app.config["ADMIN_PASSWORD"]
    )

    from .routes import api
    app.register_blueprint(api)

    return app
