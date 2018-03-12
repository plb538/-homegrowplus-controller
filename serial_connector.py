#!/usr/bin/env python

import sys
from nanpy import ArduinoApi, SerialManager

# Connect to Arduino
def connectToArduino():
    try:
        con = SerialManager()
        api = ArduinoApi(connection = con)
        return api
    except Exception as e:
        print "Failed to connect to Arduino"
        print e
        sys.exit(1)


def readPins():
	pass


def flipPinState(api, pin):
    print "Flipped pin"
    return
    if api.digitalRead(pin) == True:
        api.digitalWrite(pin, api.LOW)
    else:
        api.digitalWrite(pin, api.HIGH)
    print "Pin {} state: {}".format(pin, api.digitalRead(pin))


def quantize(value, orig_scale, new_scale, precision):
    print "Original value: {}".format(value)
    result = round(float(value)*(float(new_scale)/float(orig_scale)), precision)
    print "Quantized value: {}".format(result)
    return result


def remap(x, in_min, in_max, out_min, out_max):
	return (x-in_min)*(out_max - out_min) / (in_max - in_min) + out_min


