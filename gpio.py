#!/usr/bin/env python

import RPi.GPIO as io
import dbConnector as dbc
from flask import Flask, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

### Useful stuff
# Use pin numbers as inputs
#GPIO.setmode(GPIO.BOARD)
#GPIO.setmode(GPIO.BCM)

# Setup outpu
#GPIO.setup(pin, GPIO.OUT)

# Setup input using internal pull up resistor
#GPIO.setup(pin, GPIO.IN, pull_up_down_GPIO.PUD_UP)

# True = high
#GPIO.output(pin,True)

# Clears all pins
#GPIO.cleanup()

#puslewave = GPIO.PWM(pin, hertz)
#pulsewave.start(duty_cycle)
#pulsewave.ChangeDutyCycle(duty_cycle)
#pulsewave.ChangeFrequency(hertz)
#pulsewave.stop()

#Desired Endpoints:
#"/sensors/lights"
#"/sensors/fluids"
#"/sensors/pumps"
#"/control/pumps"
#"/control/lights"
#"/management/schedule"


if __name__ == "__main__":
    io.setwarnings(False)
    io.setmode(io.BOARD)

    print "Starting"
    try:
        dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
       # app.run(host='0.0.0.0')
    except Exception as e:
        print e
    #finally:
    #    io.cleanup()

