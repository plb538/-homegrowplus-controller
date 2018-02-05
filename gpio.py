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

@app.route("/sensors/light")
def getLights():
    return jsonify(
        {'number':'1', 'status':'on'},
        {'number':'2', 'status':'off'}
    ), 200

@app.route("/sensors/fluids")
def getFluids():
    return jsonify(
    {'name':'cleanwater', 'level':'74'},
    {'name':'drainwater', 'level':'12'},
    {'name':'nitrogen', 'level':'91'},
    {'name':'phosphorus', 'level':'87'},
    {'name':'potassium', 'level':'55'},
    {'name':'acid', 'level':'43'},
    {'name':'base', 'level':'83'},
    {'name':'mixer', 'level':'3'}
    ), 200

@app.route("/sensors/pumps")
def getPumps():
    return jsonify(
    {'name':'cleanwater', 'status':'off'},
    {'name':'drainwater', 'status':'off'},
    {'name':'nitrogen', 'status':'off'},
    {'name':'phosphorus', 'status':'off'},
    {'name':'potassium', 'status':'off'},
    {'name':'acid', 'status':'off'},
    {'name':'base', 'status':'off'},
    {'name':'mixer', 'status':'on'}
    ), 200

@app.route("/control/light")
def setLight():
    print "Light Control NYI"
    return jsonify(), 200

@app.route("/control/pump")
def setPump():
    print "Pump Control NYI"
    return jsonify(), 200

@app.route("/management/schedule")
def setSchedule():
    print "Pump Control NYI"
    return jsonify(), 200

if __name__ == "__main__":
    io.setwarnings(False)
    io.setmode(io.BOARD)

    print "Starting"
    try:
        dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
       # app.run(host='0.0.0.0')
    except Exception as e:
        print e
    finally:
        io.cleanup()

