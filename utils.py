import hashlib, uuid, ldap, time
from datetime import datetime
from flask import current_app, make_response, jsonify, abort

#create HTTP responses for app
def create_response(status_code, url, method, message):
    responseObject = {
        'status_code': status_code,
        'url': '{}'.format(url),
        'method': '{}'.format(method),
        'message': '{}'.format(message)
        }
    return responseObject

#convert types
def convert(data):
    if isinstance(data, bytes):  return data.decode()
    if isinstance(data, dict):   return dict(map(convert, data.items()))
    if isinstance(data, tuple):  return tuple(map(convert, data))
    if isinstance(data, list):   return list(map(convert, data))
    return data

#callback for kafka producer
def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        current_app.logger.error('Message delivery failed: {}'.format(err))
    else:
        current_app.logger.info('Message delivered to {} [{}] at offset {}'.format(msg.topic(), msg.partition(), msg.offset()))

'''
Deprecated due to architectural reasons. But still code may be useful
'''
#extract schema from registry
#def get_schema_from_registry(schema_registry_host, schema_registry_port, topic_name, topic_prefix='value'):
#    registry_schemas = CachedSchemaRegistryClient({'url': 'http://{}:{}'.format(schema_registry_host, schema_registry_port)})
#    extracted_schema = registry_schemas.get_latest_schema("{}-{}".format(topic_name, topic_prefix))[1]
#    return extracted_schema

#generate kafka producer event dict
#def generate_kafka_event(event_name, source_system, master_flow, attributes):
#    created_at = datetime.now()
#    hash_string = "{} {} {}".format(event_name, source_system, master_flow, str(created_at))
#    trace_id = hashlib.md5(hash_string.encode())
#    kafka_event = {
#        "eventName": "{}".format(event_name),
#        "eventId": "{}".format(uuid.uuid4()),
#        "traceId": "{}".format(trace_id.hexdigest()),
#        "sourceSystem": "{}".format(source_system),
#        "createdAt": "{}".format(created_at),
#        "masterFlow": "{}".format(master_flow),
#        "attributes": attributes
#    }
#    return kafka_event

#connect to ldap
def connect_ldap(login, password):
    try:
        connect = ldap.initialize(current_app.config['LDAP_PROVIDER_URL'])
        connect.set_option(ldap.OPT_REFERRALS, 0)
        user = 'uid={},{}'.format(login, current_app.config['LDAP_BASE_DN_NPA'])
        connect.simple_bind_s(user, password)
    except ldap.LDAPError as e:
        connect.unbind_s()
        responseObject = create_response(400, request.base_url, request.method, 'LDAP NPA Error: {}'.format(e))
        current_app.logger.error(responseObject)
        abort(make_response(jsonify(responseObject), 400))
    current_app.logger.info('LDAP connection success')
    return connect

#verify user to ldap
def verify_user_ldap(user, passd):
    username = user.upper()
    user_string = 'uid=' + username + ',' + current_app.config['LDAP_BASE_DN_USER']
    connect = connect_ldap(current_app.config['LDAP_NPA_USER'], current_app.config['LDAP_NPA_PASSWORD'])
    current_app.logger.info('Verify user: {} in LDAP Container'.format(username))
    result = connect.search_s(current_app.config['LDAP_BASE_DN_DD'], ldap.SCOPE_SUBTREE, '(uniqueMember=*' + username + '*)', current_app.config['LDAP_DISPLAY_ATTR'])
    if not result:
        responseObject = create_response(400, request.base_url, request.method, 'User {} cannot be found in LDAP Container.'.format(username))
        current_app.logger.error(responseObject)
        abort(make_response(jsonify(responseObject), 400))
    else:
        current_app.logger.info('Login user: {}.'.format(username))
        try:
            connect_user = connect.simple_bind_s(user_string, passd)
        except ldap.LDAPError as e:
            connect.unbind_s()
            responseObject = create_response(400, request.base_url, request.method, 'User {} credentials validation error: {}'.format(username, e))
            current_app.logger.error(responseObject)
            abort(make_response(jsonify(responseObject), 400))
        current_app.logger.info('Extract user {} email from LDAP.'.format(username))
        try:
            get_user_mail_cn = connect.search_s(user_string, ldap.SCOPE_SUBTREE, current_app.config['LDAP_CRITERIA_GENERIC'], current_app.config['LDAP_DISPLAY_ATTR_MAIL'])
            get_user_mail = convert(get_user_mail_cn)
        except ldap.LDAPError as e:
            connect.unbind_s()
            responseObject = create_response(400, request.base_url, request.method, 'User {} mail extraction error: {}'.format(username, e))
            current_app.logger.error(responseObject)
            abort(make_response(jsonify(responseObject), 400))
    current_app.logger.info('Results for {}: '.format(username) + str(get_user_mail[0][0]) +  ' : ' + str(get_user_mail[0][1]))
    return get_user_mail[0][1]

