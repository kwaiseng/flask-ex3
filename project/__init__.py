from flask import Blueprint
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import S3_BUCKET, S3_KEY, S3_SECRET, SECRET_KEY, SQL_Host, SQL_User, SQL_Password, URI
from .filters import datetimeformat, file_type
from flask_bootstrap import Bootstrap


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = URI


    Bootstrap(app)
    app.secret_key = 'secret'
    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.jinja_env.filters['file_type'] = file_type
    
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User
    from .models import Entry 

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))


    # blueprint for s3 routes in our app
    from .s3 import s3 as s3_blueprint
    app.register_blueprint(s3_blueprint)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app