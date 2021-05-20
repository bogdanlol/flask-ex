FROM centos/python-36-centos7

EXPOSE 8080

USER 1001

RUN pip install --upgrade pip

# Install pip requirements
ADD requirements.txt /opt/app-root/src/requirements.txt

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:8081", "wsgi:application"]
