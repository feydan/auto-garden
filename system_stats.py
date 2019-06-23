import sys, psutil, datetime, paho.mqtt.client as mqtt, json
from dotenv import load_dotenv
from time import gmtime, strftime
import os

# Get env variables
load_dotenv()
mqtt_host = os.getenv('MQTT_HOST')
mqtt_system_topic = os.getenv('MQTT_SYSTEM_TOPIC')

def getCPUtemperature():
        try:
                res = os.popen('vcgencmd measure_temp').readline()
                tmp1 = res.replace("temp=","")
                tmp1 = tmp1.replace("'","")
                tmp1 = tmp1.replace("C","")
                #print tmp1
                return tmp1
        except:
                return 0

def bytes2human(n):
# http://code.activestate.com/recipes/577972-disk-usage/
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


cputemp = int(float(getCPUtemperature()))

currtime = strftime("%Y-%m-%d %H:%M:%S")

cpupercent = psutil.cpu_percent(interval=1)
vmem = psutil.virtual_memory().percent
diskusage =  psutil.disk_usage('/').percent
disktotal = bytes2human( psutil.disk_usage('/').total )

payload = {
    'timestamp': currtime,
    'cpu_usage': cpupercent,
    'virtual_memory': vmem,
    'disk_usage': diskusage,
    'cpu_temperature': cputemp,
    'disk_total': disktotal,
}

#mqttuser = <redacted mqtt user name>
#mqttpwd = <redacted mqtt user password>

client = mqtt.Client()
#client.username_pw_set(mqttuser, mqttpwd)
client.connect(mqtt_host, 1883, 60)

payload_json = json.dumps(payload)

print(payload_json)

persistant_data = False

client.publish(mqtt_system_topic, payload_json, 0, persistant_data)
client.disconnect()

sys.exit()