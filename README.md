# auto-garden
Automatic garden watering system using Raspberry Pi.

## Setup
git clone this project to your Raspberry Pi

`pipe install -r requirements.txt`

Edit the following variables in water_the_garden.py

- `control_gpio_pin` - change this to whatever pin you are using to control your relay or switch
- `hours_per_week` - change this dictionary to reflect how long you want to water each week for the given month (links for how to calculate this below)
- `days_per_week` - how many days per week you will be watering - this is used to calculate how long to water for a given day (i.e. if watering two days a week, each script run, divide hours_per_week by 2)

## Running the watering script
`python3 water_the_garden.py`

## Adding the script to be run with cron on a schedule
Sacramento has a watering ordinance to only water two days per week and only between the hours of 7pm and 10am.
My two days are Tuesday and Thursday.  I setup my `crontab -e` to run at 5am Tuesday and Thursday (replace `<username>`, replace path if necessary):
```bash
0 5 * * 2,4 python3 /home/<username>/auto-garden/water_the_garden.py >> /home/<username>/auto-garden/water_the_garden.log 2>&1
```

## MQTT support (optional)
This script can also publish how long you watered the garden on each script run to an MQTT broker, which you can then use to track your system over time.  I'm currently piping this data in Elasticsearch and graphing in Kibana.  I may include setup instructions for this system in the future.

To configure this rename the `.env.sample` file to `.env` and specify the topic and hostname of your mqtt broker.

## Track weather
To add weather support, add this to your crontab:
```bash
*/5 * * * * python3 /home/<username>/auto-garden/track_weather.py
```

## Track system statistics
To add system statistics support, add this to your crontab:
```bash
*/1 * * * * python3 /home/<username>/auto-garden/system-stats.py
```

## Garden specs

| Label                  | Value         |
| -------------------    |--------------:|
| Square Feet            | 143           |
| Emitters               | 106           |
| Flow Rate (per emitter)| 0.5 gal/hr    |
| Crop Coefficient       | 0.6           |
| Density Coefficient    | 1             |
| Exposure Factor        | 1             |
| Efficiency             | 0.9           |
| Base hr/week           | 1.12          |

### ETo's:
ETo's: https://cimis.water.ca.gov/App_Themes/images/etozonemap.jpg

Hours per week calculation: https://ucanr.edu/sites/scmg/files/30917.pdf

| Month         | ETo     | Hours per week |
| ------------- |--------:|---------------:|
| January       | 1.55    | 1.7            |
| Februray      | 2.24    | 2.46           |
| March         | 3.72    | 4.1            |
| April         | 5.10    | 5.6            |
| May           | 6.82    | 7.5            |
| June          | 7.80    | 8.58           |
| July          | 8.68    | 9.54           |
| August        | 7.75    | 8.5            |
| September     | 5.70    | 6.27           |
| October       | 4.03    | 4.4            |
| November      | 2.10    | 2.3            |
| December      | 1.55    | 1.7            |
