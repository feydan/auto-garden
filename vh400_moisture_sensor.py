#!/usr/bin/env python3

import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
# from threading import RLock    #  May be needed if we end up multiplexing readings with a 16:1 analog mux

# Get env variables
load_dotenv()
mqtt_host = os.getenv('MQTT_HOST')
mqtt_moisture_topic = os.getenv('MQTT_MOISTURE_TOPIC')

class VH400MoistureSensor(object):
    """
    This class supports the Vegetronix VH400 MoistureSensor
    """

    ADS1115 = 0x01

    def __init__(self, i2c_addr=0x48, pin=None, gain=4096, sps=256, readings_to_average=1):
        """
        A Vegetronix VH400 MoistureSensor.

        Some notes from https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/blob/master/Adafruit_ADS1x15/ads1x15_ex_singleended.py

            Select the gain
              gain = 2/3  # +/- 6.144V
              gain = 1  # +/- 4.096V
              gain = 2  # +/- 2.048V
              gain = 4  # +/- 1.024V
              gain = 8   # +/- 0.512V
              gain = 16   # +/- 0.256V

            Select the sample rate
              sps = 8    # 8 samples per second
              sps = 16   # 16 samples per second
              sps = 32   # 32 samples per second
              sps = 64   # 64 samples per second
              sps = 128  # 128 samples per second
              sps = 250  # 250 samples per second
              sps = 475  # 475 samples per second
              sps = 860  # 860 samples per second

            Possible ADS1x15 i2c address: 0x48, 0x48, 0x4a, 0x4b
            Our default is 0x49  This will probably be hard-coded on the board.

            ADS1015 = 0x00  # 12-bit ADC
            ADS1115 = 0x01	# 16-bit ADC

        :param i2c_addr: i2c address of the ADS1115 chip
        :type i2c_addr: hex
        :param pin: Which ADC do we read when talking to this sensor?
        :type pin: int
        :param gain: Input gain.  This shouldn't be changed from 4096 as the VH400 has a 0-3v output
        :type gain: int
        :param sps: How many samples per second will the ADC take?  Lower = less noise, Higher = faster readings.
        :type sps: int
        :param readings_to_average: How many readings to we average before returning a value
        :type readings_to_average: int
        """
        ads = ADS.ADS1015(busio.I2C(board.SCL, board.SDA))
        ads.gain = gain

        self._i2c_addr = i2c_addr
        self._pin = pin
        self._gain = gain
        self._sps = sps
        self._chan = AnalogIn(ads, ADS.P0)
        self.readings_to_average = readings_to_average

    @property
    def percent(self):
        """
        Return the Volumetric Water Content (VWC) % of the soil

        VH400 Piecewise Curve:

            Most curves can be approximated with linear segments of the form:

            y= m*x-b,

            where m is the slope of the line

            The VH400's Voltage to VWC curve can be approximated with 4 segments of the form:

            VWC= m*V-b

            where  V is voltage.

            m= (VWC2 - VWC1)/(V2-V1)

            where V1 and V2 are voltages recorded at the respective VWC levels of VWC1 and VWC2.
            After m is determined, the y-axis intercept coefficient b can be found by inserting one of the end points into the equation:

            b= m*v-VWC

            Voltage Range	Equation
            0 to 1.1V	VWC= 10*V-1
            1.1V to 1.3V	VWC= 25*V- 17.5
            1.3V  to 1.82V	VWC= 48.08*V- 47.5
            1.82V to 2.2V	VWC= 26.32*V- 7.89

        :return: float
        """
        v = self.raw_voltage
        res = 0
        if 0.0 <= v <= 1.1:
            res = 10 * v - 1
        elif 1.1 < v <= 1.3:
            res = 25 * v - 17.5
        elif 1.3 < v <= 1.82:
            res = 48.08 * v - 47.5
        elif 1.82 < v:
            res = 26.32 * v - 7.89
        if res < 0:
            return 0
        else:
            return res * 1.5  # Scale result to 100% when entire green stick is submerged in water

    @property
    def raw_voltage(self):
        """
        Return the raw sensor voltage.  Average readings before returning the value

        :return: float
        """
        reading = 0.0
        for _i in range(self.readings_to_average):
            reading += self._chan.voltage
        return reading / self.readings_to_average / 1000.0


if __name__ == "__main__":

    sensor0 = VH400MoistureSensor(pin=0)
    payload = {
        voltage: sensor0.raw_voltage
        percent: sensor0.percent
    }
    print("Raw voltage: %s" % payload.voltage)
    print("Percent: %s" % payload.percent)
    
    # Publish to mqtt if it is configured
    if mqtt_host is not None:
        import paho.mqtt.publish as publish
        publish.single(mqtt_moisture_topic, json.dumps(payload), hostname=mqtt_host)
