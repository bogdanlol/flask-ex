# Openshift quickstart: Flask

This is a [Flask](http://flask.pocoo.org/) project that you can use as the starting point to develop your own and deploy it on an [OpenShift](https://github.com/openshift/origin) cluster.

The steps in this document assume that you have access to an OpenShift deployment that you can deploy applications on.

## Table of Contents

1. [Description](#description)
2. [Files in this repository](#files-in-this-repository)
3. [Notes](#notes)
4. [Development using Docker](#development-using-docker)
5. [Testing](#testing)
6. [Deployment](#deployment)
    1. [Local Openshift Cluster](#local-openshift-cluster) 
    2. [Remote Openshift Cluster](#remote-openshift-cluster)
    3. [Deploying using application templates](#deploying-using-an-application-template)
        1. [Create the PostgreSQL service](#create-the-postgresql-service)
        2. [Create the Webapp service](#create-the-webapp-service)
    4. [Without an application template](#without-an-application-template)
7. [Debugging Openshift](#debugging-openshift)
8. [Logs](#logs)
9. [Special Environment Variables](#special-environment-variables)
10. [One-off command execution](#one-off-command-execution)
11. [Future](#TODO)

## Description

This is a minimal Flask `1.0.2` project. It was created with these steps:

2. Manually install Flask and other dependencies
3. Load automatically all the env variables starting with `APP_`
3. `pip freeze > requirements.txt`
3. Configure `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PORT`, `DB_SERVICE_NAME`, `DB_ENGINE` and `FLASK_APP` entries
4. Display a hello world with some info

From this initial state you can:
* continue the development of your Flask project
* update settings to suit your needs
* install more Python libraries and add them to the `requirements.txt` file

## Files in this repository

Apart from the regular files  (`app/`, `wsgi.py`), this repository contains:

```
Dockerfile                  - Docker file to run the application 
docker-compose.yml          - Docker Compose file to run application and services 
migrations/                 - Application database migrations if needed 
tests/                      - Application tests 

openshift/                  - OpenShift-specific files
└── templates               - Application templates

requirements.txt            - List of dependencies
web-variables.env.sample    - Application sample configuration
```

## Notes

`[container]` was added to the commands that need to be run inside a container.
If it is not specified, by default it will be on the local machine.

## Development using Docker

To develop locally this project you can use `Docker` and `Docker Compose`

1. Fork this repo and clone your fork:

    `git clone https://github.com/renefs/flask-ex.git`

2. Rename the `web-variables.env.sample` file to `web-variables.env`
3. Build the Docker image:

    `docker-compose build`

4. Run the Docker image and PostgreSQL services:

    `docker-compose up`

5. Open your browser and go to `http://127.0.0.1:8080`. 
You will be greeted with a welcome page.

## Testing

```bash
docker-compose run web bash
[container] pytest
```

## Deployment

To follow the next steps, you need to be logged in to an OpenShift cluster and
 to have an OpenShift project where you can work on.

### Local Openshift cluster

Sometimes it is recommended to test a deployment on a local Openshift cluster first, 
as it won't affect your production infraestructure and it will be faster.

You can have your own Openshift cluster running locally for testing purposes 
with the following command:

```bash
oc cluster up
```

Once up, follow the instructions on the screen to access the console and login like 
in a remote cluster.

You can shutdown the cluster running:

```bash
oc cluster down
```

### Remote Openshift Cluster

You can directly login on your cluster with the following command:

```bash
oc login <your_cluster_url>
```


### Deploying using an application template

Once you are logged in your cluster, the easiest way to run your application is 
from the command line with the following commands:

#### Create the PostgreSQL service

```bash
oc new-app openshift/templates/postgres.json
```

or specifying `DATABASE_USER`, `DATABASE_NAME` and `DATABASE_PASSWORD`

```bash
oc new-app openshift/templates/postgres.json \
-p SOURCE_REPOSITORY_URL=<your repository location> \
-p DATABASE_USER=<your_db_user> \
-p DATABASE_NAME=<your_db_name> \
-p DATABASE_PASSWORD=<your_db_password>
```

#### Create the Webapp service

```bash
oc new-app openshift/templates/webapp.json
```


The directory `openshift/templates/` contains OpenShift application templates 
that you can add to your OpenShift project with:

    oc create -f openshift/templates/<TEMPLATE_NAME>.json

After adding your templates, you can go to your OpenShift web console, 
browse to your project and click the create button. Create a new app from 
one of the templates that you have just added.

Adjust the parameter values to suit your configuration. Most times you can just 
accept the default values, however you will probably want to 
set the `GIT_REPOSITORY` parameter to point to your fork and the `APP_DB_*` 
parameters to match your database configuration.


### Without an application template

Templates give you full control of each component of your application.
Sometimes your application is simple enough and you don't want to bother with templates. In that case, you can let OpenShift inspect your source code and create the required components automatically for you:

```bash
$ oc new-app centos/python-36-centos7~https://github.com/renefs/flask-ex
imageStreams/python-36-centos7
imageStreams/flask-ex
buildConfigs/flask-ex
deploymentConfigs/flask-ex
services/flask-ex
A build was created - you can run `oc start-build flask-ex` to start it.
Service "flask-ex" created at 172.30.16.213 with port mappings 8080.
```

You can access your application by browsing to the service's IP address and port.


## Debugging Openshift
    
Your application will be built and deployed automatically. 
If that doesn't happen, you can debug your build:

```bash
oc get builds
# take build name from the command above
oc logs build/<build-name>
```

And you can see information about your deployment too:

    oc describe dc/webapp

In the web console, the overview tab shows you a service, by 
default called "flask-example", that encapsulates all pods running your 
Flask application. You can access your application by browsing to the 
service's IP address and port.  You can determine these by running

    oc get svc

## Logs

By default your Flask application is served with gunicorn and 
configured to output its access log to stderr.
You can look at the combined stdout and stderr of a given pod with this command:

    oc get pods         # list all pods in your project
    oc logs <pod-name>

This can be useful to observe the correct functioning of your application.


## Special environment variables

### APP_DEBUG

Whether the application will run on debug mode or not.

### APP_CONFIG

You can fine tune the gunicorn configuration through the 
environment variable `APP_CONFIG` that, when set, should point to a 
config file as documented [here](http://docs.gunicorn.org/en/latest/settings.html).

### APP_SECRET_KEY

When using one of the templates provided in this repository, this 
environment variable has its value automatically generated. 
For security purposes, make sure to set this to a random string as 
documented [here](https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-SECRET_KEY).


### FLASK_APP

Will point to the wsgi.py file. It is needed to run Flask CLI commands.

## One-off command execution

At times you might want to manually execute some command in the 
context of a running application in OpenShift.

You can do all that by using regular CLI commands from OpenShift.

Here is how you would run a command in a pod specified by label:

1. Inspect the output of the command below to find the name of a 
pod that matches a given label:

        oc get pods -l <your-label-selector>

2. Open a shell in the pod of your choice. Because of how the images produced
  with CentOS and RHEL work currently, we need to wrap commands with `bash` to
  enable any Software Collections that may be used (done automatically inside
  every bash shell).

        oc exec -p <pod-name> -it -- bash

3. Finally, execute any command that you need and exit the shell.

Related GitHub issues:
1. https://github.com/GoogleCloudPlatform/kubernetes/issues/8876
2. https://github.com/openshift/origin/issues/2001


## Data persistence

You can deploy this application without a configured database in 
your OpenShift project, in which case Flask will use a temporary 
SQLite database that will live inside your application's container, 
and persist only until you redeploy your application.

After each deploy you get a fresh, empty, SQLite database. 
That is fine for a first contact with OpenShift and perhaps 
Flask, but sooner or later you will want to persist your data across deployments.

To do that, you should add a properly configured database server or 
ask your OpenShift administrator to add one for you. 
Then use `oc env` to update the `DATABASE_*` environment variables in 
your DeploymentConfig to match your database settings.

Redeploy your application to have your changes applied, and open the 
welcome page again to make sure your application is successfully 
connected to the database server.


## Looking for help

If you get stuck at some point, or think that this document needs 
further details or clarification, you can give feedback and look for 
help using the channels mentioned in [the OpenShift Origin repo](https://github.com/openshift/origin), or by filing an issue.

## TODO
   - Permit adding files to connector post (and file validation) - Done
   - Add logger- Done
   - Add logging 
   - Get all connectors status - Done
   - Add Restplus - Done
   - Add Config file to match template one
   - Update Dockerfile & DockerCompose
   - Create unit testing if neeeded
   - Add certificates if needed 
   - Multi Cluster investigation
   - Worker properties file 
   - Pass Properties(azure keystore value)
   
## License

This code is dedicated to the public domain to the maximum extent 
permitted by applicable law, pursuant to [CC0](http://creativecommons.org/publicdomain/zero/1.0/).
