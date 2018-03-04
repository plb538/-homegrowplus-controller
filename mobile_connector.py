#!/usr/bin/env python

import sys
import time
import dbConnector as dbc
import serial_connector as sc
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


@app.route("/sensors/lights")
def getLights():
    print "Get received on lights -- fetching from DB (NYI)"
    return jsonify(
        {'number':'1', 'status':'on'},
        {'number':'2', 'status':'off'}
    ), 200


@app.route("/sensors/fluids", methods=['GET'])
def getFluids():
    print "Get received on fluids -- fetching from DB"
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM sensors.fluids""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200


@app.route("/sensors/pumps", methods=['GET'])
def getPumps():
    print "Get received on pumps -- fetching from DB"
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM sensors.pumps""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200


@app.route("/control/lights", methods=['POST'])
def setLight():
    print "Calling setLight()"
    sc.flipPinState(api, light_control_pin_0)
    return jsonify(), 200


@app.route("/control/pumps", methods=['POST'])
def setPump():
    print "Set received on pump -- Activating pump ", request.json['pump']
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""UPDATE sensors.pumps SET status = {} WHERE name = '{}'""".format(request.json['on'], request.json['pump']))
    con.commit()
    dbc.disconnectFromDB(con)
    return jsonify(), 200


@app.route("/management/schedule")
def setSchedule():
    print "Set received on schedule -- Saving new version to DB (NYI)"
    return jsonify(), 200


if __name__ == "__main__":
    print "Starting mobile_connector.py"
    try:
		api = sc.connectToArduino()
		# Initialize analog pins
		# Analog read = 0-1023
		# Analog write = 0-255
		pH_sensor_pin_0 = 0
		temp_sensor_pin_0 = 1

		# Initialize digital pins
		# HIGH >= 2.5V
		# Conductivity sensors either high or low (use digital pins)
		conductivity_sensor_0_pin_0 = 2
		conductivity_sensor_0_pin_1 = 3
		conductivity_sensor_1_pin_0 = 4
		conductivity_sensor_1_pin_1 = 5
		conductivity_sensor_2_pin_0 = 6
		conductivity_sensor_2_pin_1 = 7
		conductivity_sensor_3_pin_0 = 8
		conductivity_sensor_3_pin_1 = 9
		light_control_pin_0 = 13

		# Set pin modes
		api.pinMode(pH_sensor_pin_0, api.INPUT)
		api.pinMode(temp_sensor_pin_0, api.INPUT)
		api.pinMode(conductivity_sensor_0_pin_0, api.INPUT)
		api.pinMode(conductivity_sensor_0_pin_1, api.INPUT)
		api.pinMode(conductivity_sensor_1_pin_0, api.INPUT)
		api.pinMode(conductivity_sensor_1_pin_1, api.OUTPUT)
		api.pinMode(conductivity_sensor_2_pin_0, api.INPUT)
		api.pinMode(conductivity_sensor_2_pin_1, api.OUTPUT)
		api.pinMode(conductivity_sensor_3_pin_0, api.INPUT)
		api.pinMode(conductivity_sensor_3_pin_1, api.OUTPUT)
		api.pinMode(light_control_pin_0, api.OUTPUT)
		app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print e
    print "Exiting mobile_connector.py"

