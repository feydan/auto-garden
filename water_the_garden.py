import datetime
from dotenv import load_dotenv
import os
import RPi.GPIO as GPIO
import time

load_dotenv()

# GPIO pin controlling the gate or relay
control_gpio_pin = 16

mqtt_host = os.getenv('MQTT_HOST')
mqtt_topic = os.getenv('MQTT_TOPIC')

GPIO.setmode(GPIO.BCM)
GPIO.setup(control_gpio_pin, GPIO.OUT)

hours_per_month = {
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


# Gets the number of hours that we want to water.
# Finds the number of hours using the hours_per_month dictionary with the current month
# and divides by days_per_week
def get_watering_hours():
    now = datetime.datetime.now()
    month = now.strftime("%B")
    return hours_per_month[month] / days_per_week


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


if __name__ == '__main__':
    hours = get_watering_hours()
    print('Watering for ' + str(hours) + ' hours')

    start_time = time.time()

    water_the_garden(hours)

    total_time = time.time() - start_time
    total_time_hours = total_time/3600

    print('Watered for ' + str(total_time_hours) + ' hours')

    # Publish to mqtt if it is configured
    if mqtt_host is not None:
        import paho.mqtt.publish as publish

        publish.single(mqtt_topic, total_time_hours, hostname=mqtt_host)
