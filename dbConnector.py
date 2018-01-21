#!/usr/bin/env python

from influxdb import client as influxdb


def connectToDB(host, port, username, password, database):
    try:
        db = influxdb.InfluxDBClient(host, port, username, password, database)
        print "Connected to database {}".format(database)
    except Exception as e:
        print "Connection error"


