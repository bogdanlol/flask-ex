import os
from types import MethodType
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from whitenoise import WhiteNoise
from werkzeug.contrib.fixers import ProxyFix
import requests
import json

from app.extensions import db

#for the moment hold the endpoint here 
#add configuration file and hold it there

endpoint = "http://localhost:8083"

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



    @app.route("/connectors", methods=['GET', 'POST'])
    def connectors():
        # curl --request POST 'localhost:8080/connectors' --header 'Content-Type:Application/json' --data '{"hello":"hello"}'
        if request.method == 'POST':
            content = request.get_json()
            header = {"content-type": "application/json"}
            response = requests.post(endpoint+'/connectors',data = json.dumps(content),headers= header)
            json_response = response.json()
            return jsonify(json_response)

        elif request.method == 'GET':
            response = requests.get(endpoint +'/connectors')
            return jsonify(response.content) 

    @app.route("/connectors/<name>", methods=['GET','DELETE'])
    def getConnector():
        
        return 'placeholder'


    @app.route("/connectors/<name>/<config>", methods=['GET','PUT'])
    def connectorConfig():
     
        return 'placeholder'

    @app.route("/connectors/<name>/tasks", methods=['GET'])
    def connectorTasks():
     
        return 'placeholder'

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


