Guide for local testing F055 API WRAPPER redesign

1. Download & Install confluent 5.5.2 
https://www.confluent.io/previous-versions/
2. Run Zookeeper & Kafka Server locally, followed by schema registry(optional), and Kafka Connect(Necessary)
3. Make sure to specify endpoint port in models file (it's the same one as where the kafka connect is running on your machine)
4. For testing purposes run python3 wsgi.py to be able to debug(TEMPORARY)
