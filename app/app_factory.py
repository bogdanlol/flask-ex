import os
from types import MethodType
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from whitenoise import WhiteNoise
from werkzeug.contrib.fixers import ProxyFix


from app.extensions import db


def create_app(config_filename):
    """
    Factory to create the application using a file

    :param config_filename: The name of the file that will be used for configuration.
    :return: The created application
    """
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.debug= True
    setup_db(app)

    # Add ProxyFix for HTTP headers
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # add whitenoise for static files
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='app/static/')

    print("Creating a Flask app with DEBUG: {}".format(app.debug))

    connectorsList = []

    @app.route("/connectors", methods=['GET', 'POST'])
    def connectors():
        # curl --request POST 'localhost:8080/connectors' --header 'Content-Type:Application/json' --data '{"hello":"hello"}'
        if request.method == 'POST':
            content = request.get_json()
            print(content)
            connectorsList.append(str(content))
            return jsonify(content)
        elif request.method == 'GET':
            print(connectorsList)
            connStr = ""
            for conn in connectorsList:
                connStr = connStr + conn+"\n\n"
            return jsonify(connStr)
        else:
            return 'connectors'

    return app


def setup_db(app):
    """
    Creates a database for the application
    :param app: Flask application to use
    :return:
    """
    print("Database Engine is: {}".format(app.config.get("DB_ENGINE", None)))
    if app.config.get("DB_ENGINE", None) == "postgresql":
        print("Setting up PostgreSQL database")
        app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
            app.config["DB_USER"],
            app.config["DB_PASS"],
            app.config["DB_SERVICE_NAME"],
            app.config["DB_PORT"],
            app.config["DB_NAME"]
        )
    else:
        _basedir = os.path.abspath(os.path.dirname(__file__))
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(_basedir, 'webapp.db')

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)
    db.app = app


