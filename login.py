import os
import os.path
import sqlite3
import string
import urllib
import urllib2
import hashlib
import sched
import time
import json
import threading

import cherrypy
from cherrypy.lib import auth_digest
import db_management

DB_STRING = "users.db"
logged_on = 0  # 0 = never tried to log on, 1 = success, 2 = tried and failed

listen_ip = "0.0.0.0" # 127.0.0.1 = localhost (loopback address), use 0.0.0.0 for local machine access
listen_port = 10002

class MainApp(object):

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
        data = data.replace("USERS_ONLINE", self.getList())
        data = data.replace("LIST_OF_USERS", self.showList())
        data = data.replace("MESSAGE_LIST", self.displayMessage())
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
    def report(self, username, password, location=1, ip='202.36.244.14', port=listen_port):
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
        with sqlite3.connect(DB_STRING) as c:
             c.execute("DELETE FROM user_string") # in order to avoid dupes in table
        # consider recalling every now and again? report also has to, receiveMessage also has to
        params = {'username':cherrypy.session['username'], 'password':cherrypy.session['password'],
                  'enc':cherrypy.session['enc'], 'json':cherrypy.session['json']}
        full_url = 'http://cs302.pythonanywhere.com/getList?' + urllib.urlencode(params)
        api_call = urllib2.urlopen(full_url).read()
        error_code = api_call[0] # error code is always first character in string
        api_format = api_call.replace("0, Online user list returned", "") # remove irrelevant text
        users_online = api_format.count(',') / 4 # db must insert users_online amount of times
        username_list = [None] * users_online
        if (error_code == '0'):
            for i in range(0, users_online):
                data = api_format.split() # split each user into different list element
                try:
                    username,location,ip,port,epoch_time = data[i].split(",",4)
                    with sqlite3.connect(DB_STRING) as c:
                         c.execute("INSERT INTO user_string(username, location, ip, port, lastlogin) VALUES (?,?,?,?,?)",
                         [username, location, ip, port, epoch_time])
                except:
                    return "some idiot is screwing shit up"
            return str(users_online) + " users online currently, they are:"
        else:
            return api_call

    @cherrypy.expose
    def showList(self):
        c = sqlite3.connect(DB_STRING)
        cur = c.cursor()
        cur.execute("SELECT username FROM user_string")
        user_list = cur.fetchall()
        string = str(user_list).strip('[]').replace("(u'","").replace("',)","") #  remove extra formatting from being a tuple of tuples
        return string


    @cherrypy.expose
    def logoff(self):
        params = {'username':cherrypy.session['username'], 'password':cherrypy.session['password']}
        full_url = 'http://cs302.pythonanywhere.com/logoff?' + urllib.urlencode(params)
        api_call = urllib2.urlopen(full_url).read()
        error_code = api_call[0]
        if (error_code == '0'):
            cherrypy.lib.sessions.expire()
            return "Logged out successfully!"
        else:
            return api_call

    @cherrypy.expose
    def ping(): # for other people to check me out
        return '0'

    @cherrypy.expose
    def receiveMessage(self, sender, destination, message, stamp=int(time.time())): # opt args: markdown, encoding, ecnryption, hashing, hash
        # now = time.strftime("%d-%m-%Y %I:%M %p",time.localtime(float(time.mktime(time.localtime()))))
        # threading.Timer(5.0, receiveMessage).start()
        # input_dict = json.loads()
        with sqlite3.connect(DB_STRING) as c:
             c.execute("INSERT INTO msg(sender, msg, stamp) VALUES (?,?,?)",
             [sender, message, stamp])
        print "Message received from " + sender

    @cherrypy.expose
    def sendMessage(self, message, destination): # destination arg has port info as well
        # posted data must be JSON format
        postdata = jsonEncode(cherrypy.session['username'], message, destination)
        dest = "http://" + destination + "/receiveMessage?"
        fptr = urllib2.urlopen(dest, urllib.urlencode(postdata)).read()
        print(fptr)
        fptr.close()
        print "Message sent to server."
        raise cherrypy.HTTPRedirect("/")

    def authoriseUserLogin(self,username, password, location, ip, port):
        params = {'username':username, 'password':password, 'location':location, 'ip':ip, 'port':port}
        full_url = 'http://cs302.pythonanywhere.com/report?' + urllib.urlencode(params)  #  converts to format &a=b&c=d...
        return urllib2.urlopen(full_url).read()

    def displayMessage(self):
        c = sqlite3.connect(DB_STRING)
        cur = c.cursor()
        cur.execute("SELECT sender, msg, stamp FROM msg")
        msg_list = cur.fetchall()
        print(msg_list)
        return str(msg_list)
        # string = str(user_list).strip('[]').replace("(u'","").replace("',)","") #  remove extra formatting from being a tuple of tuples
        # return string

    def jsonEncode(sender, message, destination):
        output_dict = { "sender": sender, "message": message, "destination": destination}
        data = json.dumps(output_dict)
        return data

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
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'css'
        }
    }

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': listen_ip,
                            'server.socket_port': listen_port,
                            'engine.autoreload.on': True,
                            'tools.gzip.on' : True,
                            'tools.gzip.mime_types' : ['text/*'],
                           })
    cherrypy.engine.subscribe('start', db_management.setup_users_database)
    cherrypy.engine.subscribe('start',db_management.setup_msg_table)
    cherrypy.engine.subscribe('stop', db_management.cleanup_users_database)
    cherrypy.engine.subscribe('stop', db_management.cleanup_msg_table)
    cherrypy.tree.mount(MainApp(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
    # this shit probably doesn't work
    # def reportUpdate(s):
    #     while (logged_on == 1): # call report once a minute with session credentials
    #         report(cherrypy.session['username'], cherrypy.session['password'],
    #         cherrypy.session['location'],cherrypy.session['ip'],cherrypy.session['port'])
    #         print("reported.")
    #         s.enter(1, 1, reportUpdate, ())
    #
    # s.enter(1, 1, reportUpdate, ())
    # s.run()
