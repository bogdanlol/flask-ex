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


    #CONNECTORS
    #GET /connectors
    #POST /connectors

    @app.route("/connectors", methods=['GET', 'POST'])
    def connectors():
        """
        ---
        get:
            description: Get a list of active connectors
              
        """
        # curl --request POST 'localhost:8080/connectors' --header 'Content-Type:Application/json' --data '{"hello":"hello"}'
        if request.method == 'POST':
            content = request.get_json()
            header = {"content-type": "application/json"}
            response = requests.post(endpoint+'/connectors',data = json.dumps(content),headers= header)
            json_response = response.json()
            return jsonify(json_response)

        elif request.method == 'GET':
            response = requests.get(endpoint +'/connectors')
            dt ={}
            dt['connectors'] = json.loads(response.content)
            return jsonify(dt) 
    #GET /connectors/(string:name)
    #DELETE /connectors/(string:name)
    @app.route("/connectors/<name>", methods=['GET','DELETE'])
    def getConnector(name=None):
        if request.method == 'GET':
            response = requests.get(endpoint +'/connectors/'+name)
            prettyResponse = json.loads(response.content)
            return jsonify(prettyResponse) 
        elif request.method == 'DELETE':
            response = requests.delete(endpoint+'/connectors/'+name)
            return jsonify(response.content) 


    #GET /connectors/(string:name)/config
    #PUT /connectors/(string:name)/config
    @app.route("/connectors/<name>/config", methods=['GET','PUT'])
    def connectorConfig(name=None):
        if request.method == 'GET':
            response = requests.get(endpoint +'/connectors/'+name+'/config')
            prettyResponse = json.loads(response.content)
            return jsonify(prettyResponse)
        elif request.method == 'PUT':
            content = request.get_json()
            header = {"content-type": "application/json"}
            response = requests.put(endpoint+'/connectors/'+name+'/config',data = json.dumps(content),headers= header)
            json_response = response.json()
            return jsonify(json_response)

    #GET /connectors/(string:name)/status
    #POST /connectors/(string:name)/restart

    @app.route("/connectors/<name>/status", methods=['GET'])
    def connectorStatus(name=None):
        if request.method == 'GET':
            response = requests.get(endpoint +'/connectors/'+name+'/status')
            prettyResponse = json.loads(response.content)
            return jsonify(prettyResponse)

    @app.route("/connectors/status", methods=['GET'])
    def connectorsStatus(name=None):
        if request.method == 'GET':
            response = requests.get(endpoint +'/connectors/')
            
            connectors = eval(response.content)
            cnStatus = {}
            if not connectors:
                return "no connectors"
            else: 
                for connector in connectors:
                    r = requests.get(endpoint +'/connectors/'+connector+"/status")
                    #maybe add wait time here depending where endpoint is
                    resp_dict = json.loads(r.content)
                    
                    cnStatus[connector]=resp_dict['connector']['state']

            return jsonify(cnStatus)

   #PUT /connectors/(string:name)/pause
    @app.route("/connectors/<name>/restart", methods=['POST'])
    def connectorsRestart(name=None):
        if request.method == 'POST':
            response = requests.post(endpoint+'/connectors/'+name+'/restart')
            if response.status_code == 204 or response.status_code==200:
                return "Connector " +name+ " has been restarted"
            else:
                return jsonify(response.status_code)

    #PUT /connectors/(string:name)/pause
    @app.route("/connectors/<name>/pause", methods=['PUT'])
    def connectorsPause(name=None):
        if request.method == 'PUT':
            response = requests.put(endpoint+'/connectors/'+name+'/pause')
            if response.status_code == 204 or response.status_code==200 or response.status_code==202:
                return "Connector " +name+ " has been paused"
            else:
                return jsonify(response.status_code)

    #PUT /connectors/(string:name)/resume
    @app.route("/connectors/<name>/resume", methods=['PUT'])
    def connectorsResume(name=None):
        if request.method == 'PUT':
            response = requests.put(endpoint+'/connectors/'+name+'/resume')
            if response.status_code == 204 or response.status_code==200 or response.status_code==202:
                return "Connector " +name+ " has been resumed"
            else:
                return jsonify(response.status_code)



    #TASKS
    #GET /connectors/(string:name)/tasks
    @app.route("/connectors/<name>/tasks", methods=['GET'])
    def connectorTasks(name=None):
        if request.method == 'GET':
            response = requests.get(endpoint +'/connectors/'+name+'/tasks')
            prettyResponse = json.loads(response.content)
            return jsonify(prettyResponse)

    #GET /connectors/(string:name)/tasks
    @app.route("/connectors/<name>/tasks/<id>/status", methods=['GET'])
    def connectorTasksStatus(name=None,id=None):
        if request.method == 'GET':
            response = requests.get(endpoint +'/connectors/'+name+'/tasks/'+id+'/status')
            prettyResponse = json.loads(response.content)
            return jsonify(prettyResponse)

    #POST /connectors/(string:name)/tasks/(int:taskid)/restart
    @app.route("/connectors/<name>/tasks/<id>/restart", methods=['POST'])
    def connectorTaskRestart(name=None,id=None):
        if request.method == 'POST':
            response = requests.post(endpoint +'/connectors/'+name+'/tasks/'+id+'/status')
            if response.status_code == 204 or response.status_code==200 or response.status_code==202:
                return "Connector " +name+ "'s task "+id+" has been resumed"
            else:
                return jsonify(response.status_code)
            
    #TOPICS
    #GET /connectors/(string:name)/topics
    @app.route("/connectors/<name>/topics", methods=['GET'])
    def connectorTopics(name=None):
        if request.method == 'GET':
            response = requests.get(endpoint +'/connectors/'+name+'/topics')
            prettyResponse = json.loads(response.content)
            return jsonify(prettyResponse)

    #PUT /connectors/(string:name)/topics/reset
    @app.route("/connectors/<name>/reset", methods=['PUT'])
    def connectorsTopicsReset(name=None):
        if request.method == 'PUT':
            response = requests.put(endpoint+'/connectors/'+name+'/reset')
            if response.status_code == 204 or response.status_code==200 or response.status_code==202:
                return "Connector " +name+ " has been reset"
            else:
                return jsonify(response.status_code)


    #Connector Plugins
    #GET /connector-plugins/
    @app.route("/connector-plugins/", methods=['GET'])
    def connectorPlugins():
        if request.method == 'GET':
            response = requests.get(endpoint +'/connector-plugins/')
            prettyResponse = json.loads(response.content)
            return jsonify(prettyResponse)

    #PUT /connector-plugins/(string:name)/config/validate
    @app.route("/connector-plugins/<name>/config/validate", methods=['PUT'])
    def connectorsPluginsConfigValidate(name=None):
        if request.method == 'PUT':
            response = requests.put(endpoint+'/connector-plugins/'+name+'/config/validate')
          
            return jsonify(response.content)

    
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


