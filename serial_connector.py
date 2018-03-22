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


def readPin(api, pin, t):
    try:
        if t == "a":
            return api.analogRead(pin)
        elif t == "d":
            return api.digitalRead(pin)
    except Exception as e:
        print "Failed to read pin: {}".format(pin)
        print e


def turnOn(api, pin, t, duty=255):
    try:
        if t == "a":
            api.analogWrite(pin, duty)
        elif t == "d":
            api.digitalWrite(pin, api.HIGH)
    except Exception as e:
        print "Failed to turn on pin: {}{}".format(t, pin)
        print e


def turnOff(api, pin, t, duty=0):
    try:
        if t == "a":
            api.analogWrite(pin, duty)
        elif t == "d":
            api.digitalWrite(pin, api.LOW)
    except Exception as e:
        print "Failed to turn off pin: {}{}".format(t, pin)


def quantize(value, new_max, new_min=0, orig_max=1023, orig_min=0, precision=2):
    #print "Original value: {}".format(value)
    result = round(((float(value) - float(orig_min))*(float(new_max) - float(new_min)) / (float(orig_max) - float(orig_min)) + float(new_min)), precision)
    #print "Quantized value: {}".format(result)
    return result

