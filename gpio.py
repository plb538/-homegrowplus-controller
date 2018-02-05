#!/usr/bin/env python

import RPi.GPIO as io
import dbConnector as dbc
from flask import Flask, request, jsonify
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

@app.route("/sensors/fluids", methods=['GET'])
def getFluids():
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM sensors.fluids""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200

@app.route("/sensors/pumps", methods=['GET'])
def getPumps():
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM sensors.pumps""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200

@app.route("/control/light")
def setLight():
    print "Light Control NYI"
    return jsonify(), 200

@app.route("/control/pumps", methods=['POST'])
def setPump():
    print "Pump Control NYI"
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""UPDATE sensors.pumps SET status = {} WHERE name = '{}'""".format(request.json['on'], request.json['pump']))
    con.commit()
    dbc.disconnectFromDB(con)
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
        app.run(host='0.0.0.0')
    except Exception as e:
        print e
    finally:
        io.cleanup()

