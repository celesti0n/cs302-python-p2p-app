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
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("DROP TABLE user_string")
