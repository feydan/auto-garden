from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from datetime import datetime
from elasticsearch import Elasticsearch
import os
import json

load_dotenv()
mqtt_host = os.getenv('MQTT_HOST')

channelSubs = "#"

# {
#   <namespace>: {
#       'index': '<indexName>',
#       'topic_field': '<field name for topic>',
#       'topic_blacklist': [<list of topic strings>]
#   }
# }
# defaults: { <namespace>: {'index': '<namespace>', 'topic_field': 'topic', 'topic_blacklist': []} }
namespace_config = {
    'miflora': {
        'index': 'garden_sensor',
        'topic_field': 'device',
        'topic_blacklist': ['$announce'],
    }
}

default_index_prefix = 'garden_'


# Called when connected
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(channelSubs)


# Called when a message is received
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

    parts = msg.topic.split('/')
    namespace = parts[0]
    topic = parts[1]

    config = get_namespace_config(namespace)

    if topic in config['topic_blacklist']:
        return

    payload = json.loads(msg.payload)

    now = datetime.utcnow()
    payload['timestamp'] = now

    payload[config['topic_field']] = topic
    print("Sending to Elasticsearch " + config['index'] + " index: " + str(payload))
    try:
        res = es.index(index=config['index'], doc_type='_doc', body=payload)
        print(res['result'])
    except Exception as e:
        print(str(e))


def get_namespace_config(namespace):
    fields = ('index', 'topic_field', 'topic_blacklist')
    if namespace in namespace_config and all(field in namespace_config[namespace] for field in fields):
        return namespace_config[namespace]

    if namespace not in namespace_config:
        namespace_config[namespace] = {}

    config = namespace_config[namespace]

    if 'index' not in config:
        config['index'] = default_index_prefix + namespace

    if 'topic_field' not in config:
        config['topic_field'] = 'topic'

    if 'topic_blacklist' not in config:
        config['topic_blacklist'] = []

    return config


# Connects to Elasticsearch on localhost:9200
es = Elasticsearch()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_host, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
