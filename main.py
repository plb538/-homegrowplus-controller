#!/usr/bin/env python

import sys
import time
import json
import db_connector as dbc
import serial_connector as sc
import Adafruit_DHT
import RPi.GPIO as gpio
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


@app.route("/info/plants", methods=['GET'])
def getPlants():
    try:
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        cur.execute("""SELECT * FROM plants""")
        results = cur.fetchall()
    except Exception as e:
        print "Failed to get plants"
        print e
        return jsonify(), 503
    finally:
        dbc.disconnectFromDB(con)
        return jsonify(results), 200


@app.route("/control/lights", methods=['POST'])
def setLightStatus():
    try:
        if request.json['on'] is True:
            sc.turnOn(api, light_0, "d")
        else:
            sc.turnOff(api, light_0, "d")
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        cur.execute("""UPDATE lights SET status = {} WHERE id = {}""".format(request.json['on'], request.json['light']))
    except Exception as e:
        print "Failed to set light status"
        print e
        return jsonify, 503
    finally:
        con.commit()
        dbc.disconnectFromDB(con)
        return jsonify(), 200


# Modifies the boolean status of a pump
@app.route("/control/pumps", methods=['POST'])
def setPumpStatus():
    try:
        results, code = getPumpSensors()
        results = json.loads(results.response[0])
        results = dict([((el[0]), float(el[1])) for el in results])
        t = "d"
        if request.json['on'] == True:
            if (request.json['pump'] == "clean_water" or request.json['pump'] == "nutrients" or request.json['pump'] == "acid" or request.json['pump'] == "base") and results['mixer_full'] > 2.5:
                print "Tried to pump with mixer too full"
                return jsonify(), 503
            elif request.json['pump'] == "drain_water":
                if results['drain_water'] > 0:
                    print "Tried to pump with drain too full"
                    return jsonify(), 503
            elif request.json['pump'] == "mixer":
                if results['mixer_empty'] < 2.5:
                    print "Tried to pump with mixer empty"
                    return jsonify(), 503
            elif request.json['pump'] == "mister":
                if results['clean_water'] == 0:
                    print "Tries to use mister while clean water is low"
                    return jsonify(), 503
            elif request.json['pump'] == "drain_out":
                pass
            elif (request.json['pump'] != "drain_water" or request.json['pump'] != "mixer" or request.json['pump'] != "mister" or request.json['pump'] != "drain_out") and results[request.json['pump']] == 0:
                print "Tried to pump with bad low fluid level on {}".format(request.json['pump'])
                return jsonify(), 503
            sc.turnOn(api, pins["{}_pump".format(request.json['pump'])], t)
        else:
            sc.turnOff(api, pins["{}_pump".format(request.json['pump'])], t)
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format(request.json['on'], request.json['pump']))
    except Exception as e:
        print "Failed to set pump status"
        print e
    finally:
        con.commit()
        dbc.disconnectFromDB(con)
        return jsonify(), 200


def startMixer():
    try:
    	results, code = getPumpSensors()
	results = json.loads(results.response[0])
	results = dict([((el[0]), float(el[1])) for el in results])
	if results['mixer_empty'] < 2.5:
	    print "Mixer it too low. Failed to start the mixer motor"
	    return jsonify(), 503
	sc.turnOn(api, mixer_0, "d")
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        cur.execute("""UPDATE mixers SET status = {} WHERE name = '{}'""".format("true", "mixer_0"))
        con.commit()
	dbc.disconnectFromDB(con)
        time.sleep(5)
	sc.turnOff(api, mixer_0, "d")
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        cur.execute("""UPDATE mixers SET status = {} WHERE name = '{}'""".format("false", "mixer_0"))
        con.commit()
    except Exception as e:
        print "Failed to set mixer status"
        print e
    finally:
        dbc.disconnectFromDB(con)
        return jsonify(), 200


@app.route("/add/plants", methods=['POST'])
def addPlants():
    try:
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        cur.execte("""DROP TABLE plants""")
        con.commit()
        cur.execute("""CREATE TABLE plants (name varchar(50) primary key, datePlanted varchat(50) not null)""")
        con.commit()
        cur.execute("""INSERT INTO plants (name, datePlanted) values ('{}', '{}')""".format(request.json[0]['name'], request.json[0]['datePlanted']))
        cur.execute("""INSERT INTO plants (name, datePlanted) values ('{}', '{}')""".format(request.json[1]['name'], request.json[1]['datePlanted']))
        cur.execute("""INSERT INTO plants (name, datePlanted) values ('{}', '{}')""".format(request.json[2]['name'], request.json[2]['datePlanted']))
    except Exception as e:
        print "Failed to add plants"
        print e
    finally:
        con.commit()
        dbc.disconnectFromDB(con)
        return jsonify(), 200


@app.route("/management/schedule", methods=['POST'])
def setSchedule():
    try:
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        cur.execute("""UPDATE schedules set waterOnTime = {}, waterCyclePeriod = {}, lightOnTime = {}, lightCyclePeriod = {} where day = '{}'""".format(int(request.json['waterOnTime']), int(request.json['waterCyclePeriod']), int(request.json['lightOnTime']), int(request.json['lightCyclePeriod']), request.json['day']))
        startSchedule()
    except Exception as e:
	print "Failed to set schedule"
	print e
    finally:
        con.commit()
        dbc.disconnectFromDB(con)
        return jsonify(), 200


@app.route("/management/schedule", methods=['GET'])
def getSchedule():
    try:
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        cur.execute("""SELECT * FROM schedules""")
        results = cur.fetchall()
        dbc.disconnectFromDB(con)
        return jsonify(), 200
    except Exception as e:
	print "Failed to get schedule"
	print e


@app.route("/control/schedule", methods=['GET'])
def startSchedule():
    try:
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        cur.execute("""SELECT * FROM schedules where day = '{}'""".format(request.json['day']))
        results = cur.fetchall()
        dbc.disconnectFromDB(con)
        waterOnTime = float(request.json['waterOnTime'])
        waterCyclePeriod = float(request.json['waterCyclePeriod'])
        lightOnTime = float(request.json['lightOnTime'])
        lightCyclePeriod = float(request.json['lightCyclePeriod'])
        pw = Process(target=runWaterSchedule, args=(api, waterOnTime, waterCyclePeriod,))
        pw.start()
        pl = Process(target=runLightSchedule, args=(api, lightOnTime, lightCyclePeriod,))
        pl.start()
        #pw.join()
        #pl.join()
        return jsonify(), 200
    except Exception as e:
	print "Failed to start schedule"
	print e


def runWaterSchedule(api, waterOnTime, waterCyclePeriod):
    while True:
	try:
	    print "Running water schedule in background"
    	    results, code = getPumpSensors()
            results = json.loads(results.response[0])
            results = dict([((el[0]), float(el[1])) for el in results])
            pump_results, code = getPumpStatuses()
            pump_results = json.loads(pump_results.response[0])
            pump_results = dict([((el[0]), el[1]) for el in pump_results])
	    if results['mixer_empty'] < 2.5:
                print "Mixer is empty"
        	sc.turnOff(api, mixer_pump, "d")
                cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', 'mixer'))
		con.commit()
		dbc.disconnectFromDB(con)
		fillMixer()
	    else:
                print "Mixer not empty"
	      	if pump_results['mixer'] == False:
	    	    sc.turnOn(api, mixer_pump, "d")
                    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('true', 'mixer'))
		    con.commit()
		    dbc.disconnectFromDB(con)
		    time.sleep(waterOnTime)
                pump_results, code = getPumpStatuses()
                pump_results = json.loads(pump_results.response[0])
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
		if pump_results['mixer'] == True:
		    sc.turnOff(api, mixer_pump, "d")
		    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', 'mixer'))
		    con.commit()
		    dbc.disconnectFromDB(con)
		    time.sleep(waterCyclePeriod)
                pump_results, code = getPumpStatuses()
                pump_results = json.loads(pump_results.response[0])
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                if pump_results['drain_out'] == False:
                    sc.turnOn(api, drain_out_pump, "d")
                    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('true', 'drain_out'))
                    con.commit()
                    dbc.disconnectFromDB(con)
                    time.sleep(int(0.5*waterOnTime))
                pump_results, code = getPumpStatuses()
                pump_results = json.loads(pump_results.response[0])
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                if pump_results['drain_out'] == True:
                    sc.turnOff(api, drain_out_pump, "d")
                    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', 'drain_out'))
                    con.commit()
                    dbc.disconnectFromDB(con)
	except Exception as e:
	    print "Failed to run the water schedule"
	    print e


def runLightSchedule(api, lightOnTime, lightCyclePeriod):
    while True:
        try:
            print "Running light schedule in background"
            results, code = getLightStatuses()
	    results = json.loads(results.response[0])
	    results = dict([(float(el[0]), el[1]) for el in results])
	    if results[0] == False:
                sc.turnOn(api, light_0, "d")
                cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""UPDATE lights SET status = '{}' WHERE id = {}""".format('true', 0))
                con.commit()
                dbc.disconnectFromDB(con)
                time.sleep(lightOnTime)
            results, code = getLightStatuses()
            results = json.loads(results.response[0])
            results = dict([(float(el[0]), el[1]) for el in results])
            if results[0] == True:
            	sc.turnOff(api, light_0, "d")
            	cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
            	cur.execute("""UPDATE lights SET status = '{}' WHERE id = {}""".format('false', 0))
            	con.commit()
            	dbc.disconnectFromDB(con)
            	time.sleep(lightCyclePeriod)
        except Exception as e:
            print "Failed to run the light schedule"
            print e


def fillMixer():
    while True:
	try:
            print "Filling mixer"
            cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
            cur.execute("""SELECT * FROM conductivity_sensors""")
            results = cur.fetchall()
            dbc.disconnectFromDB(con)
            results = dict([((el[0]), float(el[1])) for el in results])
            if results['mixer_full'] > 2.5:
        	print "Mixer is full"
                startMixer()
        	break
            else:
                print "Mixer still not full"
                cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM pumps""")
                pump_results = cur.fetchall()
                dbc.disconnectFromDB(con)
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM conductivity_sensors""")
                results = cur.fetchall()
                dbc.disconnectFromDB(con)
                results = dict([((el[0]), float(el[1])) for el in results])
	        if pump_results['clean_water'] == False and results['mixer_full'] < 2.5:
                    print "Filling mixer with clean water"
	            sc.turnOn(api, clean_water_pump, "d")
	            cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
	    	    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('true', 'clean_water'))
	    	    con.commit()
	    	    dbc.disconnectFromDB(con)
	    	    time.sleep(3)
	    	cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM pumps""")
                pump_results = cur.fetchall()
                dbc.disconnectFromDB(con)
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                if pump_results['clean_water'] == True:
		    sc.turnOff(api, clean_water_pump, "d")
		    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', 'clean_water'))
		    con.commit()
		    dbc.disconnectFromDB(con)
		cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM pumps""")
                pump_results = cur.fetchall()
                dbc.disconnectFromDB(con)
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM conductivity_sensors""")
                results = cur.fetchall()
                dbc.disconnectFromDB(con)
                results = dict([((el[0]), float(el[1])) for el in results])
                if pump_results['nutrients'] == False and results['mixer_full'] < 2.5:
                    print "Filling mixer with nutrients"
		    sc.turnOn(api, nutrients_pump, "d")
	            cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('true', 'nutrients'))
		    con.commit()
		    dbc.disconnectFromDB(con)
		    time.sleep(1)
		cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM pumps""")
                pump_results = cur.fetchall()
                dbc.disconnectFromDB(con)
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                if pump_results['nutrients'] == True:
	            sc.turnOff(api, nutrients_pump, "d")
		    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', 'nutrients'))
		    con.commit()
		    dbc.disconnectFromDB(con)
		cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM pumps""")
                pump_results = cur.fetchall()
                dbc.disconnectFromDB(con)
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM conductivity_sensors""")
                results = cur.fetchall()
                dbc.disconnectFromDB(con)
                results = dict([((el[0]), float(el[1])) for el in results])
                if pump_results['acid'] == False and results['mixer_full'] < 2.5:
                    print "Filling mixer with acid"
		    sc.turnOn(api, acid_pump, "d")
		    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('true', 'acid'))
		    con.commit()
		    dbc.disconnectFromDB(con)
		    time.sleep(1)
		cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM pumps""")
                pump_results = cur.fetchall()
                dbc.disconnectFromDB(con)
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                if pump_results['acid'] == True:
		    sc.turnOff(api, acid_pump, "d")
		    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', 'acid'))
		    con.commit()
		    dbc.disconnectFromDB(con)
		cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM pumps""")
                pump_results = cur.fetchall()
                dbc.disconnectFromDB(con)
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM conductivity_sensors""")
                results = cur.fetchall()
                dbc.disconnectFromDB(con)
                results = dict([((el[0]), float(el[1])) for el in results])
                if pump_results['base'] == False and results['mixer_full'] < 2.5:
                    print "Filling mixer with base"
		    sc.turnOn(api, base_pump, "d")
		    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('true', 'base'))
		    con.commit()
		    dbc.disconnectFromDB(con)
		    time.sleep(1)
		cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
                cur.execute("""SELECT * FROM pumps""")
                pump_results = cur.fetchall()
                dbc.disconnectFromDB(con)
                pump_results = dict([((el[0]), el[1]) for el in pump_results])
                if pump_results['base'] == True:
		    sc.turnOff(api, base_pump, "d")
		    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', 'base'))
		    con.commit()
		    dbc.disconnectFromDB(con)
        except Exception as e:
            print "Failed to auto fill mixer"
            print e


def poll(api):
    while True:
        try:
            cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
            cur.execute("""SELECT * FROM pumps""")
            results = cur.fetchall()
            dbc.disconnectFromDB(con)
            results = dict([((el[0]), el[1]) for el in results])
	    cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
	    #pH = (-1.129*(float(sc.quantize(sc.readPin(api, pH_sensor_0, "a"), 5))) + 9.774)
            #if pH is not None:
    	    #    cur.execute("""UPDATE ph_sensors SET value = {} WHERE name = '{}'""".format(pH, "ph_sensor_0"))
	    hum, temp = Adafruit_DHT.read(Adafruit_DHT.DHT11, temp_sensor_0)
	    if hum is not None and temp is not None:
	        cur.execute("""UPDATE temp_sensors SET tempurature = {}, humidity = {} WHERE name = '{}'""".format(float(temp), float(hum), "temp_sensor_0"))
	    val = sc.readPin(api, clean_water_conductivity_sensor, "d")
	    if val is not None:
		cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(val, "clean_water"))
	    if val == 0:
		print "Safety shutdown for clean_water"
		if results['clean_water'] == True:
		    sc.turnOff(api, clean_water_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "clean_water"))
		if results['mister'] == True:
		    sc.turnOff(api, mister_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "mister"))
	    val = sc.readPin(api, drain_water_conductivity_sensor, "d")
	    if val is not None:
	        cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(val, "drain_water"))
	    if val > 0:
		print "Safety shutdown for drain_water"
		if results['drain_water'] == True:
		    sc.turnOff(api, drain_water_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "drain_water"))
	    val = sc.quantize(sc.readPin(api, nutrient_conductivity_sensor, "a"), 5)
	    if val is not None:
		cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(val, "nutrients"))
	    if val < 2.5:
		print "Safety shutdown for nutrients"
		if results['nutrients'] == True:
		    sc.turnOff(api, nutrients_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "nutrients"))
	    val = sc.quantize(sc.readPin(api, acid_conductivity_sensor, "a"), 5)
	    if val is not None:
		cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(val, "acid"))
	    if val < 2.5:
		print "Safety shutdown for acid"
		if results['acid'] == True:
	    	    sc.turnOff(api, acid_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "acid"))
	    val = sc.quantize(sc.readPin(api, base_conductivity_sensor, "a"), 5)
	    if val is not None:
		cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(val, "base"))
	    if val < 2.5:
		print "Safety shutdown for base"
		if results['base'] == True:
		    sc.turnOff(api, base_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "base"))
	    val = sc.quantize(sc.readPin(api, mixer_empty_conductivity_sensor, "a"), 5)
	    if val is not None:
		cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(val, "mixer_empty"))
	    if val < 2.5:
		print "Safety shutdown for mixer"
		if results['mixer'] == True:
		    sc.turnOff(api, mixer_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "mixer"))
	    val = sc.quantize(sc.readPin(api, mixer_full_conductivity_sensor, "a"), 5)
	    if val is not None:
		cur.execute("""UPDATE conductivity_sensors SET value = {} WHERE name = '{}'""".format(val, "mixer_full"))
	    if val > 2.5:
		print "Safety shutdown due to mixer overflow"
		if results['clean_water'] == True:
		    sc.turnOff(api, clean_water_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "clean_water"))
		if results['nutrients'] == True:
		    sc.turnOff(api, nutrients_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "nutrients"))
		if results['acid'] == True:
		    sc.turnOff(api, acid_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "acid"))
		if results['base'] == True:
		    sc.turnOff(api, base_pump, "d")
		    cur.execute("""UPDATE pumps SET status = {} WHERE name = '{}'""".format('false', "base"))
	except Exception as e:
	    print "Could not poll data from the Arduino"
	    print e
	finally:
            con.commit()
	    dbc.disconnectFromDB(con)
	    time.sleep(2)


if __name__ == "__main__":
    print "Starting"
    try:
        gpio.setmode(gpio.BCM)
        temp_sensor_0 = 18
        gpio.setup(temp_sensor_0, gpio.IN)

        api = sc.connectToArduino()
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        for table in {'pumps', 'lights', 'mixers'}:
            cur.execute("""UPDATE {} SET status = false""".format(table))
        con.commit()
        dbc.disconnectFromDB(con)

	pH_sensor_0 = 0
	#temp_sensor_0 = 1
        nutrient_conductivity_sensor = 1
	acid_conductivity_sensor = 2
        base_conductivity_sensor = 3
        mixer_empty_conductivity_sensor = 4
        mixer_full_conductivity_sensor = 5

	clean_water_conductivity_sensor = 2
	drain_water_conductivity_sensor = 3
	drain_out_pump = 4
	light_0 = 5
        mixer_0 = 6
        mixer_pump = 7
        mister_pump = 8
        clean_water_pump = 9
	drain_water_pump = 10
	nutrients_pump = 11
	acid_pump = 12
	base_pump = 13

	pins = {"pH_sensor_0": pH_sensor_0, "light_0": light_0, "mixer_0": mixer_0, "mixer_pump": mixer_pump, "mister_pump": mister_pump, "clean_water_conductivity_sensor": clean_water_conductivity_sensor, "drain_water_conductivity_sensor": drain_water_conductivity_sensor, "nutrient_conductivity_sensor": nutrient_conductivity_sensor, "acid_conductivity_sensor": acid_conductivity_sensor, "base_conductivity_sensor": base_conductivity_sensor, "mixer_empty_conductivity_sensor":
                mixer_empty_conductivity_sensor, "mixer_full_conductivity_sensor": mixer_full_conductivity_sensor, "clean_water_pump": clean_water_pump, "drain_water_pump": drain_water_pump, "nutrients_pump": nutrients_pump, "acid_pump": acid_pump, "base_pump": base_pump, "drain_out_pump": drain_out_pump}

	# Set pin modes
	api.pinMode(pH_sensor_0, api.INPUT)
	#api.pinMode(temp_sensor_0, api.INPUT)
        api.pinMode(light_0, api.OUTPUT)
        api.digitalWrite(light_0, api.LOW)
        api.pinMode(mixer_0, api.OUTPUT)
        api.digitalWrite(mixer_0, api.LOW)
        api.pinMode(clean_water_conductivity_sensor, api.INPUT)
        api.pinMode(drain_water_conductivity_sensor, api.INPUT)
        api.pinMode(nutrient_conductivity_sensor, api.INPUT)
	api.pinMode(acid_conductivity_sensor, api.INPUT)
        api.pinMode(base_conductivity_sensor, api.INPUT)
        api.pinMode(mixer_empty_conductivity_sensor, api.INPUT)
        api.pinMode(mixer_full_conductivity_sensor, api.INPUT)
        api.pinMode(clean_water_pump, api.OUTPUT)
        api.digitalWrite(clean_water_pump, api.LOW)
        api.pinMode(drain_water_pump, api.OUTPUT)
        api.digitalWrite(drain_water_pump, api.LOW)
        api.pinMode(nutrients_pump, api.OUTPUT)
        api.digitalWrite(nutrients_pump, api.LOW)
	api.pinMode(acid_pump, api.OUTPUT)
        api.digitalWrite(acid_pump, api.LOW)
	api.pinMode(base_pump, api.OUTPUT)
        api.digitalWrite(base_pump, api.LOW)
	api.pinMode(mixer_pump, api.OUTPUT)
        api.digitalWrite(mixer_pump, api.LOW)
	api.pinMode(mister_pump, api.OUTPUT)
        api.digitalWrite(mister_pump, api.LOW)
        api.pinMode(drain_out_pump, api.OUTPUT)
        api.digitalWrite(drain_out_pump, api.LOW)

	p = Process(target=poll, args=(api,))
	p.start()
	app.run(host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        p.join()
    finally:
        gpio.cleanup()
        for pin in pins:
            sc.turnOff(api, pins[pin], "a")
            sc.turnOff(api, pins[pin], "d")
        cur, con = dbc.connectToDB('localhost', 5432, 'postgres', 'postgres', 'homegrowplus')
        for table in {'pumps', 'lights', 'mixers'}:
            cur.execute("""UPDATE {} SET status = false""".format(table))
        con.commit()
        dbc.disconnectFromDB(con)
    print "Exiting"

