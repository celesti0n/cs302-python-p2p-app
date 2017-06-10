# This file exists to hold all the helper functions which solely retrieve things from the database.
import sqlite3

DB_STRING = "users.db"

def getProfilePic(user):
    c = sqlite3.connect(DB_STRING)
    cur = c.cursor()
    cur.execute("SELECT picture FROM profiles WHERE profile_username=?",
                [user])
    pic = cur.fetchone()
    if not pic:  # no pic found
        return 'http://imgur.com/oymng0G.jpg'  # return default pic, fort logo
    else:
        return ''.join(pic)  # tuple to string

def checkOnline(user):
    c = sqlite3.connect(DB_STRING)
    cur = c.cursor()
    cur.execute("SELECT lastlogin FROM user_string WHERE username=?", [user])
    credentials = cur.fetchone()
    if not credentials:  # empty found
        return ''
    else:
        return 'Online now!'
