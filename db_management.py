import json
import time
import sqlite3
import threading

DB_STRING = "users.db"

def setup_users_database():
    """
    Create the user_string table in the database on server startup
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("CREATE TABLE user_string (user_id INTEGER PRIMARY KEY, username, location, ip, port, lastlogin)")
        # add public key argument to this later when required

def cleanup_users_database():
    """
    Destroy 'user_string' table when server shuts down.
    Maybe take this out later.
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("DROP TABLE user_string")

def setup_total_users_table():
    """
    Create the total_users table in the database
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("CREATE TABLE total_users (user_id INTEGER PRIMARY KEY, username)")
        # add public key argument to this later when required

def cleanup_total_users_table():

    with sqlite3.connect(DB_STRING) as con:
        con.execute("DROP TABLE total_users")
