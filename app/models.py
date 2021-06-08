import os
from flask import Flask, request, jsonify,abort,current_app
from app.connectorSchema import connectorSchema as connectorSchema
from jsonschema import validate
from werkzeug.utils import secure_filename
import requests 
import json 
from utils import *



endpoint = "http://localhost:8083"

class Connectors():
    #get list of available connectors
    def getConnectors():
        try:
            response= requests.get(endpoint +'/connectors')
            dt ={}
            dt['connectors'] = json.loads(response.content)
            return jsonify(dt)
        except Exception as e:
            responseObject = create_response(400, request.base_url, request.method, "error encountered {0}".format(e))
            current_app.logger.error(responseObject)
            abort(make_response(jsonify(responseObject), 400))


    #PostConnector
    def postConnector(temp_folder):
        if not request.files:
                content = request.get_json()
                header = {"content-type": "application/json"}
                response = requests.post(endpoint+'/connectors',data = json.dumps(content),headers= header)
                json_response = response.json()
                return jsonify(json_response)
        else:
            file = request.files['file']
            if file :
                filename = secure_filename(file.filename)
                file.save(os.path.join(temp_folder, filename))
                content=''
                with open(os.path.join(temp_folder, filename),'r') as f:
                    try :    
                        content = f.read()
                        validate(content,connectorSchema)
                    except Exception as e : 
                        return(e)                       
                os.remove(os.path.join(temp_folder, filename))
                header = {"content-type": "application/json"}
                
                response = requests.post(endpoint+'/connectors',data = content,headers= header)
                json_response = response.json()
                return jsonify(json_response)

    #get specific connector
    def getConnector(name=None):
        response = requests.get(endpoint +'/connectors/'+name)
        prettyResponse = json.loads(response.content)
        return jsonify(prettyResponse) 

    #delete specific connector
    def deleteConnector(name=None):
        response = requests.delete(endpoint+'/connectors/'+name)
        return jsonify(response.content) 

    def getConnectorConfig(name=None):
        response = requests.get(endpoint +'/connectors/'+name+'/config')
        prettyResponse = json.loads(response.content)
        return jsonify(prettyResponse)

    def putConnectorConfig(name=None):
        content = request.get_json()
        header = {"content-type": "application/json"}
        response = requests.put(endpoint+'/connectors/'+name+'/config',data = json.dumps(content),headers= header)
        json_response = response.json()
        return jsonify(json_response)

    def getConnnectorStatus(name=None):
        response = requests.get(endpoint +'/connectors/'+name+'/status')
        prettyResponse = json.loads(response.content)
        return jsonify(prettyResponse)
    def getConnectorsStatus():
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
        
    def postConnectorRestart(name=None):
        response = requests.post(endpoint+'/connectors/'+name+'/restart')
        if response.status_code == 204 or response.status_code==200:
            return "Connector " +name+ " has been restarted"
        else:
            return jsonify(response.status_code)

    def putConnectorPause(name=None):
        response = requests.put(endpoint+'/connectors/'+name+'/pause')
        if response.status_code == 204 or response.status_code==200 or response.status_code==202:
            return "Connector " +name+ " has been paused"
        else:
            return jsonify(response.status_code)
    def getConnectorResume(name=None):
        response = requests.put(endpoint+'/connectors/'+name+'/resume')
        if response.status_code == 204 or response.status_code==200 or response.status_code==202:
            return "Connector " +name+ " has been resumed"
        else:
            return jsonify(response.status_code)

class Tasks():
    def getConnectorTasks(name=None):
        response = requests.get(endpoint +'/connectors/'+name+'/tasks')
        prettyResponse = json.loads(response.content)
        return jsonify(prettyResponse)

    def getConnectorTasksStatus(name=None,id=None):
        response = requests.get(endpoint +'/connectors/'+name+'/tasks/'+id+'/status')
        prettyResponse = json.loads(response.content)
        return jsonify(prettyResponse)

    def postConnectorTaskRestart(name=None,id=None):
        response = requests.post(endpoint +'/connectors/'+name+'/tasks/'+id+'/status')
        if response.status_code == 204 or response.status_code==200 or response.status_code==202:
            return "Connector " +name+ "'s task "+id+" has been resumed"
        else:
            return jsonify(response.status_code)

class Topics():
    def getConnectorTopics(name=None):
        response = requests.get(endpoint +'/connectors/'+name+'/topics')
        prettyResponse = json.loads(response.content)
        return jsonify(prettyResponse)

    def putConnectorsTopicsReset(name=None):
        response = requests.put(endpoint+'/connectors/'+name+'/reset')
        if response.status_code == 204 or response.status_code==200 or response.status_code==202:
            return "Connector " +name+ " has been reset"
        else:
            return jsonify(response.status_code)

class ConnectorPlugins():
    def getConnectorPlugins():
        response = requests.get(endpoint +'/connector-plugins/')
        prettyResponse = json.loads(response.content)
        return jsonify(prettyResponse)

    def putConnectorsPluginsConfigValidate(name=None):
        response = requests.put(endpoint+'/connector-plugins/'+name+'/config/validate')
        return jsonify(response.content)
