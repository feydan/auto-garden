from collections import defaultdict
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import *
from dotenv import load_dotenv
import json
import os
import requests
from statistics import mean
from urllib3.exceptions import HTTPError

# Get env variables
load_dotenv()
open_weather_app_id = os.getenv('OPEN_WEATHER_APP_ID')
zip_code = os.getenv('ZIP_CODE')
mqtt_host = os.getenv('MQTT_HOST')
mqtt_weather_topic = os.getenv('MQTT_WEATHER_TOPIC')


# Gets the current weather and stores it in a file as well as publishes it to mqtt if configured
def get_weather():
    try:
        url = "https://api.openweathermap.org/data/2.5/weather?zip=%s,us&units=metric&APPID=%s" % (zip_code, open_weather_app_id)
        current_weather = requests.get(url).json()
        print(str(current_weather))

        payload = {
            'temperature': current_weather['main']['temp'],
            'pressure': current_weather['main']['pressure'],
            'humidity': current_weather['main']['humidity'],
            'wind_speed': current_weather['wind']['speed'] if 'wind' in current_weather else 0,
            'cloud_cover': current_weather['clouds']['all'] if 'clouds' in current_weather else 0,
            'rain_1h': current_weather['rain']['1h'] if 'rain' in current_weather else 0,
            'rain_3h': current_weather['rain']['3h'] if 'rain' in current_weather else 0,
        }

        # Publish to mqtt if it is configured
        if mqtt_host is not None:
            import paho.mqtt.publish as publish
            publish.single(mqtt_weather_topic, json.dumps(payload), hostname=mqtt_host)

        store_rain_data(payload['rain_1h'])

    except HTTPError:
        print('Could not get weather')
        pass


# Stores weather data in a file as json with keys being the timestamps
def store_rain_data(rain_1h):
    now = datetime.now()

    # Get stored rain data
    rain_file = get_rain_file()

    # Remove any data 2 days old
    two_days_ago = now - relativedelta(days=2)
    for date_string in list(rain_file.keys()):
        if parser.parse(date_string) < two_days_ago:
            del(rain_file[date_string])

    # Add this reading to the json
    now_formatted = datetime.strftime(now, '%Y-%m-%d %H:%M:00')
    rain_file[now_formatted] = rain_1h

    # Save the file
    with open('rain.json', 'w') as f:
        f.write(json.dumps(rain_file))


# We are using open weather map to get rain forecast data
# Since historical data is not free, we are storing the rain forecast over the past two days
# If any of the last two days had >= 5mm rain, return true
def rain_in_past_two_days():
    now = datetime.now()

    # Get stored rain data
    rain_file = get_rain_file()

    # We should have 1h rain data every 5 minutes
    # We want to take the average for every hour and then sum to get the total rain per day
    # rain_by_day_and_hour gives us a list of readings every hour for 1 day ago and 2 days ago
    two_days_ago = now - relativedelta(days=2)
    one_day_ago = now - relativedelta(days=1)
    rain_by_day_and_hour = {1: defaultdict(list), 2: defaultdict(list)}
    for date_string, rain_1h in rain_file.items():
        dt = parser.parse(date_string)
        if dt >= one_day_ago:
            rain_by_day_and_hour[1][dt.hour].append(rain_1h)
        elif dt >= two_days_ago:
            rain_by_day_and_hour[2][dt.hour].append(rain_1h)

    rain_total_two_days_ago = sum(map(mean, rain_by_day_and_hour[2].values()))
    rain_total_one_day_ago = sum(map(mean, rain_by_day_and_hour[1].values()))

    return rain_total_two_days_ago >= 5 or rain_total_one_day_ago >= 5


# Gets the rain file and json decodes it
def get_rain_file():
    rain_file = {}
    if os.path.exists("rain.json"):
        with open('rain.json', 'r') as f:
            rain_file = json.loads(f.read())

    return rain_file


if __name__ == '__main__':
    get_weather()
