#!/usr/bin/env python

import psycopg2 as psql


def connectToDB(host, port, username, password, database):
    try:
        con = psql.connect(host=host, port=port, user=username, password=password, dbname=database)
        print "Connected to database {}".format(database)
        cur = con.cursor()
        return cur, con
    except Exception as e:
        print "Connection error"
        print e


def disconnectFromDB(con):
    try:
        if con is not None:
            con.close()
            print "Disconnected from database"
    except Exception as e:
        print "Could not close connection"
        print e

