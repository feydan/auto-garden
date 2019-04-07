from datetime import datetime
from dotenv import load_dotenv
import json
import os
import RPi.GPIO as GPIO
import time
from track_weather import rain_in_past_two_days

# GPIO pin controlling the gate or relay
control_gpio_pin = 16

hours_per_week = {
    "January": 1.7,
    "February": 2.46,
    "March": 4.1,
    "April": 5.6,
    "May": 7.5,
    "June": 8.58,
    "July": 9.54,
    "August": 8.5,
    "September": 6.27,
    "October": 4.4,
    "November": 2.3,
    "December": 1.7,
}

# How many days per week you will be watering
days_per_week = 2

# Get weather and mqtt variables from .env
load_dotenv()
open_weather_app_id = os.getenv('OPEN_WEATHER_APP_ID')
zip_code = os.getenv('ZIP_CODE')
mqtt_host = os.getenv('MQTT_HOST')
mqtt_topic = os.getenv('MQTT_TOPIC')

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(control_gpio_pin, GPIO.OUT)


# Gets the number of hours that we want to water.
# Finds the number of hours using the hours_per_week dictionary with the current month
# and divides by days_per_week
def get_watering_hours():
    now = datetime.now()
    month = now.strftime("%B")
    return hours_per_week[month] / days_per_week


# Waters the garden by turning the GPIO pin on for the specified number of hours
def water_the_garden(hours):
    try:
        # On
        GPIO.output(control_gpio_pin, GPIO.LOW)

        time.sleep(hours * 3600)

        # Off
        GPIO.output(control_gpio_pin, GPIO.HIGH)
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()
        pass


def publish_to_mqtt(start_time, end_time, hours):
    # Publish to mqtt if it is configured
    if mqtt_host is not None:
        import paho.mqtt.publish as publish
        payload = json.dumps({
            'time_frame': {
                'gte': start_time,
                'lte': end_time
            },
            'hours': hours
        })
        publish.single(mqtt_topic, payload, hostname=mqtt_host)


if __name__ == '__main__':
    # Check weather if configured
    if open_weather_app_id is not None and zip_code is not None and rain_in_past_two_days():
        print('Not watering because it rained in the past two days')
        publish_to_mqtt(0)

    hours = get_watering_hours()
    print('Watering for ' + str(hours) + ' hours')

    start_time = time.time()

    water_the_garden(hours)

    end_time = time.time()
    total_time = end_time - start_time
    total_time_hours = total_time/3600

    print('Watered for ' + str(total_time_hours) + ' hours')

    publish_to_mqtt(start_time, end_time, total_time_hours)
