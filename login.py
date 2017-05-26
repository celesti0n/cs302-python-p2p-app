import os
import os.path
import sqlite3
import string
import urllib
import urllib2
import hashlib
import sched
import time

import cherrypy
from cherrypy.lib import auth_digest

DB_STRING = "users.db"
logged_on = 0  # 0 = never tried to log on, 1 = success, 2 = tried and failed



class StringGenerator(object):
    #TODO: need to pass username and password as class variables? so we can reuse, esp. for getList
    #getList shouldn't need a form to input creds again. we need to store username and password creds
    #from /report to use in authenticating getList.
    @cherrypy.expose
    def index(self):
        f = open("index.html", "r")
        data = f.read()
        f.close()
        # need conditional to show error message if login failed
        if (logged_on == 2):  # 2 shows up if a failed login attempt has been made
            data = data.replace("LOGIN_STATUS", "An invalid username or password was entered. Please try again.")
        else:  # if no login attempt has been made or login successful, do not show prompt
            data = data.replace("LOGIN_STATUS", "")

        return data

    @cherrypy.expose
    def home(self):
        f = open("home.html", "r")
        data = f.read()
        f.close()
        data = data.replace("USER_NAME", cherrypy.session['username'])
        data = data.replace("SESSION_ID", cherrypy.session.id)
        s = sched.scheduler(time.time, time.sleep)
        return data

    @cherrypy.expose
    def register(self, username, password, work_id):
        #in the future need to have length checks for params
        with sqlite3.connect(DB_STRING) as c:
            c.execute("INSERT INTO user_string(session_id, username, password, work_id) VALUES (?,?,?,?)",
            [cherrypy.session.id, username, password, work_id])
        return open('home.html').read().format(name=username,sid=cherrypy.session.id)

    @cherrypy.expose
    def report(self, username, password, location=1, ip='202.36.244.13', port=80):
        hashedPassword = hash(password)  # call hash function for SHA256 encryption
        auth = self.authoriseUserLogin(username, hashedPassword, location, ip, port)
        error_code,error_message = auth.split(",")
        if (error_code == '0'):  # successful login, populate session variables
            global logged_on
            logged_on = 1
            cherrypy.session['username'] = username
            cherrypy.session['password'] = hashedPassword  # is this safe?
            cherrypy.session['location'] = location
            cherrypy.session['ip'] = ip
            cherrypy.session['port'] = port
            cherrypy.session['enc'] = 0  # change these later if deciding to use enc/json/etc.
            cherrypy.session['json'] = 0
            raise cherrypy.HTTPRedirect('/home')
        else:
            global logged_on
            logged_on = 2
            raise cherrypy.HTTPRedirect('/')  # set flag to change /index function

    @cherrypy.expose
    def getList(self):
        params = {'username':cherrypy.session['username'], 'password':cherrypy.session['password'],
                  'enc':cherrypy.session['enc'], 'json':cherrypy.session['json']}
        full_url = 'http://cs302.pythonanywhere.com/getList?' + urllib.urlencode(params)
        api_call = urllib2.urlopen(full_url).read()
        return api_call


    def authoriseUserLogin(self,username, password, location, ip, port):
        params = {'username':username, 'password':password, 'location':location, 'ip':ip, 'port':port}
        full_url = 'http://cs302.pythonanywhere.com/report?' + urllib.urlencode(params)  #  converts to format &a=b&c=d...
        return urllib2.urlopen(full_url).read()



"""class StringGeneratorWebService(object):
    exposed = True
    purely for RESTful principles.
    To create a resource on the server, use POST.
    To retrieve a resource, use GET.
    To change the state of a resource or to update it, use PUT.
    To remove or delete a resource, use DELETE.

    implement later if i can
    @cherrypy.tools.accept(media='text/plain')"""


def setup_database():
    """
    Create the user_string table in the database on server startup
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("CREATE TABLE user_string (user_id INTEGER PRIMARY KEY, session_id, username, password, work_id)")
        # move session_id out of this table later (does not belong in user info)
        # draw up the relational db with keys

def cleanup_database():
    """
    Destroy 'user_string' table when server shuts down.
    Maybe take this out later.
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("DROP TABLE user_string")

# HASHING ALGORITHM - SHA256
def hash(str):
    hashed_str = hashlib.sha256(str + 'COMPSYS302-2017').hexdigest() #hexdigest returns hex in string form, use digest for byte form
    return hashed_str




conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath(os.path.dirname(__file__)),
            'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__))
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.subscribe('start', setup_database)
    cherrypy.engine.subscribe('stop', cleanup_database)
    cherrypy.quickstart(StringGenerator(), '/', conf)
    #this shit probably doesn't work
    def reportUpdate(s):
        while (logged_on == 1): # call report once a minute with session credentials
            report(cherrypy.session['username'], cherrypy.session['password'],
            cherrypy.session['location'],cherrypy.session['ip'],cherrypy.session['port'])
            print("reported.")
            s.enter(1, 1, reportUpdate, ())

    s.enter(1, 1, reportUpdate, ())
    s.run()
