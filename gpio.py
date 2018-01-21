#!/usr/bin/env python

import RPi.GPIO as io
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

@app.route("/on")
def turnOnLED():
    io.output(12, True)
    print "LED on"
    return jsonify({'hello': 'world'}), 200


@app.route("/off")
def turnOffLED():
    io.output(12, False)
    print "LED off"
    return jsonify({'goodbye': 'world'}), 200


if __name__ == "__main__":
    io.setwarnings(False)
    io.setmode(io.BOARD)

    # Pin setup
    io.setup(12, io.OUT)

    try:
        app.run(host='0.0.0.0')
    except Exception as e:
        print e.message()
    finally:
        io.cleanup()

