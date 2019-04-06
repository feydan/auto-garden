from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from datetime import datetime
from elasticsearch import Elasticsearch
import os
import json

load_dotenv()
mqtt_host = os.getenv('MQTT_HOST')

channelSubs = "#"

miflora_namespace = 'miflora'

# Called when connected
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(channelSubs)


# Called when a message is received
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

    now = datetime.utcnow()

    payload = json.loads(msg.payload)
    payload['timestamp'] = now

    parts = msg.topic.split('/')
    namespace = parts[0]
    topic = parts[1]
    if namespace == miflora_namespace:
        payload['device'] = topic
        print("Sending to Elasticsearch garden index: " + str(payload))
        res = es.index(index="garden", doc_type="garden", body=payload)
        print(res['result'])
    else:
        payload['topic'] = topic
        print("Sending to Elasticsearch " + namespace + " index: " + str(payload))
        res = es.index(index=namespace, doc_type=namespace, body=payload)
        print(res['result'])


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
