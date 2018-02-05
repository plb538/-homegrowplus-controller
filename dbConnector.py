#!/usr/bin/env python

import psycopg2 as psql


def connectToDB(host, port, username, password, database):
    try:
        con = psql.connect(host=host, port=port, user=username, password=password, dbname=database)
        print "Connected to database {}".format(database)
        cur = con.curser()
        return cur, con
    except Exception as e:
        print "Connection error"


def disconnectFromDB(con):
    try:
        if con is not None:
            con.close()
    except Exception as e:
        print "Could not close connection"
        print e

