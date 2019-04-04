# auto-garden
Automatic garden watering system using Raspberry Pi.

## Running the watering script
`python3 water_the_garden.py`

## Adding the script to be run with cron on a schedule
Sacramento has a watering ordinance to only water two days per week and only between the hours of 7pm and 10am.
My two days are Tuesday and Thursday.  I setup my `crontab -e` to run at 5am Tuesday and Thursday (replace <username>):
```bash
0 5 * * 2,4 python3 /home/<username>/auto-garden/water_the_garden.py
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
