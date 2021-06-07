import os
from types import MethodType
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from whitenoise import WhiteNoise
from werkzeug.contrib.fixers import ProxyFix
import requests
import json
from time import sleep
from app.extensions import db
from flask_restplus import Api,Resource
from utils import *

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
    api = Api(app=app)
    ns = api.namespace('connectors', 'Connector methods -> api wrapper based on f0055')
    cpns = api.namespace('connector-plugins','Connector Plugins methods -> api wrapper on f0055')
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

    @ns.route("/", methods=['GET', 'POST'])
    class ConnectorsApi(Resource):
        def get(self):
            return Connectors.getConnectors()
        
        def post(self):
            return Connectors.postConnector(temp_folder)
    

    #GET /connectors/(string:name)
    #DELETE /connectors/(string:name)
    @ns.route("/<name>", methods=['GET','DELETE'])
    class ConnectorsApi(Resource):
        def get(self,name):
            return Connectors.getConnector(name)
        def delete(self,name):
            return Connectors.deleteConnector(name)
    

    #GET /connectors/(string:name)/config
    #PUT /connectors/(string:name)/config
    @ns.route("/<name>/config", methods=['GET','PUT'])
    class ConnectorsApi(Resource):
        def get(self,name):
            return Connectors.getConnectorConfig(name)
        def put(self,name):
            return Connectors.putConnectorConfig(name)

    #GET /connectors/(string:name)/status
    #POST /connectors/(string:name)/restart

    @ns.route("/<name>/status", methods=['GET'])
    class ConnectorsApi(Resource):
        def get(self,name):
            return Connectors.getConnnectorStatus(name)

    @ns.route("/status", methods=['GET'])
    class ConnectorsApi(Resource):
        def get(self):
            return Connectors.getConnectorsStatus()

   #PUT /connectors/(string:name)/pause
    @ns.route("/<name>/restart", methods=['POST'])
    class ConnectorsApi(Resource):
        def post(self,name):
            return Connectors.postConnectorRestart(name)

    #PUT /connectors/(string:name)/pause
    @ns.route("/<name>/pause", methods=['PUT'])
    class ConnectorsApi(Resource):
        def put(self,name):
           return Connectors.putConnectorPause(name)

    #PUT /connectors/(string:name)/resume
    @ns.route("/<name>/resume", methods=['PUT'])
    class ConnectorsApi(Resource):
        def put(self,name):
            return Connectors.getConnectorResume(name)

    #TASKS
    #GET /connectors/(string:name)/tasks
    @ns.route("/<name>/tasks", methods=['GET'])
    class TasksApi(Resource):
        def get(self,name):
            return Tasks.getConnectorTasks(name)

    #GET /connectors/(string:name)/tasks
    @ns.route("/<name>/tasks/<id>/status", methods=['GET'])
    class TasksApi(Resource):
        def get(self,name,id):
           return Tasks.getConnectorTasksStatus(name,id)

    #POST /connectors/(string:name)/tasks/(int:taskid)/restart
    @ns.route("/<name>/tasks/<id>/restart", methods=['POST'])
    class TasksApi(Resource):
        def post(self,name,id):
            return Tasks.postConnectorTaskRestart(name,id)
            
    #TOPICS
    #GET /connectors/(string:name)/topics
    @ns.route("/<name>/topics", methods=['GET'])
    class TopicsApi(Resource):
        def get(self,name):
            return Topics.getConnectorTopics(name)

    #PUT /connectors/(string:name)/topics/reset
    @ns.route("/<name>/reset", methods=['PUT'])
    class TopicsApi(Resource):
        def put(self,name):
            return Topics.putConnectorTopicsReset(name)


    #Connector Plugins
    #GET /connector-plugins/
    @cpns.route("/", methods=['GET'])
    class ConnectorPlugins(Resource):
        def get(self):
            return ConnectorPlugins.getConnectorPlugins()

    #PUT /connector-plugins/(string:name)/config/validate
    @cpns.route("/<name>/config/validate", methods=['PUT'])
    class ConnectorPlugins(Resource):
        def put(self,name):
            return ConnectorPlugins.putConnectorsPluginsConfigValidate(name)

    
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
