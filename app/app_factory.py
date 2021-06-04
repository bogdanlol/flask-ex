import os
from types import MethodType
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from whitenoise import WhiteNoise
from werkzeug.contrib.fixers import ProxyFix
import requests
import json
from time import sleep
from app.api_spec import spec
from app.extensions import db
from app.swagger import swagger_ui_blueprint, SWAGGER_URL

from app.models import Connectors, Tasks, Topics, ConnectorPlugins
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
    temp_folder = app.config['UPLOAD_FOLDER']
    print("Creating a Flask app with DEBUG: {}".format(app.debug))

   
    #CONNECTORS
    #GET /connectors
    #POST /connectors

    @app.route("/connectors", methods=['GET', 'POST'])
    def connectors():
        """
        ---
        get:
            description: Get a list of active connectors
        post:
            description: Post new Connector via json or via files
            content: application/json

        """
        # curl --request POST 'localhost:8080/connectors' --header 'Content-Type:Application/json' --data '{"hello":"hello"}'
        if request.method == 'POST':
            return Connectors.postConnector(temp_folder)

        elif request.method == 'GET':
     
            return Connectors.getConnectors()
    #GET /connectors/(string:name)
    #DELETE /connectors/(string:name)
    @app.route("/connectors/<name>", methods=['GET','DELETE'])
    def getConnector(name=None):
        if request.method == 'GET':
            return Connectors.getConnector(name)
        elif request.method == 'DELETE':
            return Connectors.deleteConnector(name)
    

    #GET /connectors/(string:name)/config
    #PUT /connectors/(string:name)/config
    @app.route("/connectors/<name>/config", methods=['GET','PUT'])
    def connectorConfig(name=None):
        if request.method == 'GET':
            return Connectors.getConnectorConfig(name)
        elif request.method == 'PUT':
            return Connectors.putConnectorConfig(name)

    #GET /connectors/(string:name)/status
    #POST /connectors/(string:name)/restart

    @app.route("/connectors/<name>/status", methods=['GET'])
    def connectorStatus(name=None):
        return Connectors.getConnnectorStatus(name)

    @app.route("/connectors/status", methods=['GET'])
    def connectorsStatus():
        return Connectors.getConnectorsStatus()

   #PUT /connectors/(string:name)/pause
    @app.route("/connectors/<name>/restart", methods=['POST'])
    def connectorsRestart(name=None):
        if request.method == 'POST':
            return Connectors.postConnectorRestart(name)

    #PUT /connectors/(string:name)/pause
    @app.route("/connectors/<name>/pause", methods=['PUT'])
    def connectorsPause(name=None):
        if request.method == 'PUT':
           return Connectors.putConnectorPause(name)

    #PUT /connectors/(string:name)/resume
    @app.route("/connectors/<name>/resume", methods=['PUT'])
    def connectorsResume(name=None):
        if request.method == 'PUT':
            return Connectors.getConnectorResume(name)

    #TASKS
    #GET /connectors/(string:name)/tasks
    @app.route("/connectors/<name>/tasks", methods=['GET'])
    def connectorTasks(name=None):
        if request.method == 'GET':
            return Tasks.getConnectorTasks(name)

    #GET /connectors/(string:name)/tasks
    @app.route("/connectors/<name>/tasks/<id>/status", methods=['GET'])
    def connectorTasksStatus(name=None,id=None):
        if request.method == 'GET':
           return Tasks.getConnectorTasksStatus(name,id)

    #POST /connectors/(string:name)/tasks/(int:taskid)/restart
    @app.route("/connectors/<name>/tasks/<id>/restart", methods=['POST'])
    def connectorTaskRestart(name=None,id=None):
        if request.method == 'POST':
            return Tasks.postConnectorTaskRestart(name,id)
            
    #TOPICS
    #GET /connectors/(string:name)/topics
    @app.route("/connectors/<name>/topics", methods=['GET'])
    def connectorTopics(name=None):
        if request.method == 'GET':
            return Topics.getConnectorTopics(name)

    #PUT /connectors/(string:name)/topics/reset
    @app.route("/connectors/<name>/reset", methods=['PUT'])
    def connectorsTopicsReset(name=None):
        if request.method == 'PUT':
            return Topics.putConnectorTopicsReset(name)


    #Connector Plugins
    #GET /connector-plugins/
    @app.route("/connector-plugins/", methods=['GET'])
    def connectorPlugins():
        if request.method == 'GET':
            return ConnectorPlugins.getConnectorPlugins()

    #PUT /connector-plugins/(string:name)/config/validate
    @app.route("/connector-plugins/<name>/config/validate", methods=['PUT'])
    def connectorsPluginsConfigValidate(name=None):
        if request.method == 'PUT':
            return ConnectorPlugins.putConnectorsPluginsConfigValidate(name)

    
    #DOCS
    with app.test_request_context():
    # register all swagger documented functions here
        for fn_name in app.view_functions:
            if fn_name == 'static':
                continue
            print(f"Loading swagger docs for function: {fn_name}")
            view_fn = app.view_functions[fn_name]
            spec.path(view=view_fn)

    @app.route("/api/swagger.json")
    def create_swagger_spec():
        return jsonify(spec.to_dict())
        
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app['ALLOWED_EXTENSIONS']
