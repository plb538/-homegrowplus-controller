#!/usr/bin/env python

import sys
import time
import json
import db_connector as dbc
import serial_connector as sc
from nanpy import DHT
from multiprocessing import Process
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


# Returns all pH sensors along with their values
@app.route("/sensors/ph", methods=['GET'])
def getPHSensors():
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM ph_sensors""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200


# Returns all tempurature sensors along with their values
@app.route("/sensors/temp", methods=['GET'])
def getTempSensors():
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM temp_sensors""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200


# Returns all conductivity sensors along with their values
@app.route("/sensors/pumps", methods=['GET'])
def getPumpSensors():
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM conductivity_sensors""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200


# Returns all pump statuses
@app.route("/control/pumps", methods=['GET'])
def getPumpStatuses():
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM pumps""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200


# Returns all mixer statuses
@app.route("/control/mixers", methods=['GET'])
def getMixerStatuses():
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM mixers""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200


# Returns all light statuses
@app.route("/control/lights", methods=['GET'])
def getLightStatuses():
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""SELECT * FROM lights""")
    results = cur.fetchall()
    dbc.disconnectFromDB(con)
    return jsonify(results), 200


@app.route("/control/lights", methods=['POST'])
def setLightStatus():
    if request.json['on'] is True:
        sc.turnOn(api, light_0, "a")
    else:
        sc.turnOff(api, light_0, "a")
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""UPDATE lights SET status = {} WHERE id = {}""".format(request.json['on'], request.json['light']))
    con.commit()
    dbc.disconnectFromDB(con)
    return jsonify(), 200


# Modifies the boolean status of a pump
@app.route("/control/pumps", methods=['POST'])
def setPumpStatus():
    results, code = getPumpSensors()
    results = json.loads(results.response[0])
    results = dict([((el[0]), float(el[1])) for el in results])
    print request.json['pump']
    t = ""
    if request.json['pump'].startswith("mi"):
        t = "a"
    else:
        t = "d"
    if (request.json['pump'] == "clean_water" or request.json['pump'] == "nutrients" or request.json['pump'] == "acid" or request.json['pump'] == "base") and results['mixer_full'] > 0:
        return jsonify(), 503
    elif request.json['pump'] == "drain_water":
        if results['drain_water'] > 0:
            return jsonify(), 503
    elif request.json['pump'] == "mixer":
        if results['mixer_empty'] == 0:
            return jsonify(), 503
    elif (request.json['pump'] != "drain_water" or request.json['pump'] != "mixer") and results[request.json['pump']] == 0:
        return jsonify(), 503
    if request.json['on'] is True:
        sc.turnOn(api, pins["{}_pump".format(request.json['pump'])], t)
    else:
        sc.turnOff(api, pins["{}_pump".format(request.json['pump'])], t)
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format(request.json['on'], request.json['pump']))
    con.commit()
    dbc.disconnectFromDB(con)
    return jsonify(), 200


# Modifies the boolean status of a mixer
@app.route("/control/mixers", methods=['POST'])
def setMixerStatus():
    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
    cur.execute("""UPDATE mixers SET status = {} WHERE name = '{}'""".format(request.json['on'], request.json['mixer']))
    con.commit()
    dbc.disconnectFromDB(con)
    return jsonify(), 200

# To do
@app.route("/management/schedule", methods=['POST'])
def setSchedule():
    #Todo set timer to fire pumps appropriately based on the schedule
    #print request.json
    #JSON = [day:daily, waterOnTime:number, waterCyclePeriod:number, lightOnTime:number, lightCyclePeriod:number]
    #print "Set received on schedule -- Saving new version to DB (NYI)"
    return jsonify(), 200

@app.route("/management/schedule", methods=['GET'])
def getSchedule():
    #print "Get received on schedule -- Saving new version to DB (NYI)"
    return jsonify(), 503


def poll(api):
    #dht = DHT(temp_sensor_0, DHT.DHT11)
    while True:
        print "polling"
        try:
            cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
            cur.execute("""UPDATE ph_sensors SET value = {} WHERE name = '{}'""".format(sc.quantize(sc.readPin(api, pH_sensor_0, "a"), 14), "ph_sensor_0"))
            #cur.execute("""UPDATE temp_sensors SET value = {} WHERE name = '{}'""".format(sc.quantize(sc.readPin(api, temp_sensor_0, "a"), 30), "temp_sensor_0"))
            val = sc.quantize(sc.readPin(api, clean_water_conductivity_sensor, "d"), 5)
            cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(val), "clean_water"))
            if val == 0:
                cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format(false, "clean_water"))
            cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(sc.quantize(sc.readPin(api, drain_water_conductivity_sensor, "d"), 5), "drain_water"))
            if val == 0:
                                 cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".          format(false, "clean_water"))
            cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(sc.quantize(sc.readPin(api, nutrient_conductivity_sensor, "d"), 5), "nutrients"))
            if val == 0:
                                 cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".          format(false, "clean_water"))
            cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(sc.quantize(sc.readPin(api, acid_conductivity_sensor, "d"), 5), "acid"))
            cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(sc.quantize(sc.readPin(api, base_conductivity_sensor, "d"), 5), "base"))
            cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(sc.quantize(sc.readPin(api, mixer_empty_conductivity_sensor, "d"), 5), "mixer_empty"))
            cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(sc.quantize(sc.readPin(api, mixer_full_conductivity_sensor, "d"), 5), "mixer_full"))
            con.commit()
        except Exception as e:
            print "Could not poll data from the Arduino"
        finally:
            dbc.disconnectFromDB(con)
            time.sleep(2)


if __name__ == "__main__":
    print "Starting"
    try:
	api = sc.connectToArduino()
        # Initialize analog pins
	# Analog read = 0-1023
	# Analog write = 0-255
	pH_sensor_0 = 0
	temp_sensor_0 = 1
        light_0 = 2
        mixer_0 = 3
        mixer_pump = 4 #Set duty to 255
        mister_pump = 5 #Set duty to 255

        # Initialize digital pins
    	# HIGH >= 2.5V
	# Conductivity sensors either high or low (use digital pins)
	clean_water_conductivity_sensor = 2
	drain_water_conductivity_sensor = 3
	nutrient_conductivity_sensor = 4
	acid_conductivity_sensor = 5
        base_conductivity_sensor = 6
        mixer_empty_conductivity_sensor = 7
        mixer_full_conductivity_sensor = 8
        clean_water_pump = 9
        drain_water_pump = 10
        nutrients_pump = 11
        acid_pump = 12
        base_pump = 13

        pins = {"pH_sensor_0": pH_sensor_0, "temp_sensor_0": temp_sensor_0, "light_0": light_0, "mixer_0": mixer_0, "mixer_pump": mixer_pump, "mister_pump": mister_pump, "clean_water_conductivity_sensor": clean_water_conductivity_sensor, "drain_water_conductivity_sensor": drain_water_conductivity_sensor, "nutrient_conductivity_sensor": nutrient_conductivity_sensor, "acid_conductivity_sensor": acid_conductivity_sensor, "base_conductivity_sensor": base_conductivity_sensor,
                "mixer_empty_conductivity_sensor": mixer_empty_conductivity_sensor, "mixer_full_conductivity_sensor": mixer_full_conductivity_sensor, "clean_water_pump": clean_water_pump,	"drain_water_pump": drain_water_pump, "nutrients_pump": nutrients_pump, "acid_pump": acid_pump, "base_pump": base_pump}

        # Set pin modes
	api.pinMode(pH_sensor_0, api.INPUT)
	api.pinMode(temp_sensor_0, api.INPUT)
	api.pinMode(light_0, api.OUTPUT)
        api.pinMode(mixer_0, api.OUTPUT)
        api.pinMode(clean_water_conductivity_sensor, api.INPUT)
        api.pinMode(drain_water_conductivity_sensor, api.INPUT)
        api.pinMode(nutrient_conductivity_sensor, api.INPUT)
	api.pinMode(acid_conductivity_sensor, api.INPUT)
        api.pinMode(base_conductivity_sensor, api.INPUT)
        api.pinMode(mixer_empty_conductivity_sensor, api.INPUT)
        api.pinMode(mixer_full_conductivity_sensor, api.INPUT)
        api.pinMode(clean_water_pump, api.OUTPUT)
        api.pinMode(drain_water_pump, api.OUTPUT)
	api.pinMode(nutrients_pump, api.OUTPUT)
	api.pinMode(acid_pump, api.OUTPUT)
	api.pinMode(base_pump, api.OUTPUT)
        api.pinMode(mixer_pump, api.OUTPUT)
	api.pinMode(mister_pump, api.OUTPUT)

        #p = Process(target=poll, args=(api,))
        #p.start()
	app.run(host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        pass
        #p.join()
    finally:
        for pin in pins:
            sc.turnOff(api, pins[pin], "a")
            sc.turnOff(api, pins[pin], "d")
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres',          'homegrowplus')
        for table in {'pumps', 'lights', 'mixers'}:
            cur.execute("""UPDATE {} SET status = false""".format(table))
        con.commit()
        dbc.disconnectFromDB(con)
    print "Exiting"

