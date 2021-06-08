Guide for local testing F055 API WRAPPER redesign

1. Download & Install confluent 5.5.2 
https://www.confluent.io/previous-versions/
2. Run Zookeeper & Kafka Server locally, followed by schema registry(optional), and Kafka Connect(Necessary)
3. Make sure to specify endpoint port in models file (it's the same one as where the kafka connect is running on your machine)
4. Make sure to set your environment for python 3.6 and run 
$ pip3 install -r requirements.txt
if it fails when trying to install ldap please install the following packages on your machine 
Debian\Ubuntu:
$ sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
RedHat\CentOS:
$ sudo yum install python-devel openldap-devel
5. For testing purposes run python3 wsgi.py to be able to debug(TEMPORARY)
