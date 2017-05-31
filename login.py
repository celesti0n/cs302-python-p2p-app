import os
import os.path
import sqlite3
import string
import urllib
import urllib2
import sched
import time
import json
import threading
import socket

import cherrypy
from cherrypy.lib import auth_digest
import db_management
import encrypt

DB_STRING = "users.db"
logged_on = 0  # 0 = never tried to log on, 1 = success, 2 = tried and failed

listen_ip = socket.gethostbyname(socket.getfqdn()) # 127.0.0.1 = localhost (loopback address), use 0.0.0.0 for local machine access
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
        return data

    @cherrypy.expose
    def report(self, username, password, location=1, ip=listen_ip, port=listen_port):
        print(ip)
        hashedPassword = encrypt.hash(password)  # call hash function for SHA256 encryption
        auth = self.authoriseUserLogin(username, hashedPassword, location, ip, port)
        error_code,error_message = auth.split(",")
        if (error_code == '0'):  # successful login, populate session variables
            global logged_on
            logged_on = 1
            cherrypy.session['username'] = username
            cherrypy.session['password'] = hashedPassword
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
    def listUsers(self):
        url = 'http://cs302.pythonanywhere.com/listUsers'
        api_call = urllib2.urlopen(url).read()
        total_users_list = api_call.split(",")
        total_users = len(total_users_list)
        print total_users_list
        for i in range(0, total_users):
            with sqlite3.connect(DB_STRING) as c:
                 c.execute("INSERT INTO total_users(username) VALUES (?)",
                 [total_users_list[i]])
        return "There are " + str(total_users) + " current users. \n" + str(total_users_list)
    
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
    def ping(self): # for other people to check me out, implement sender arg later
        print("SOMEBODY PINGED YOU!")
        return '0'

    @cherrypy.expose
    def listAPI(self):
        return '/ping /listAPI /receiveMessage [sender] [destination] [message] [stamp]'

    @cherrypy.expose
    def receiveMessage(self, sender, destination, message, stamp=int(time.time())): # opt args: markdown, encoding, ecnryption, hashing, hash
        print("checking for messages...")
        info_dict = json.loads(sender, destination, message) #decode out of json
        print(info_dict)
        if destination == cherrypy.session['username']: # the message was meant for this user
            with sqlite3.connect(DB_STRING) as c:
                 c.execute("INSERT INTO msg(sender, msg, stamp) VALUES (?,?,?)",
                 [sender, message, stamp])
            print "Message received from " + sender
        else: # message was meant for somebody else
            print("Passing this message on: " + message)
        threading.Timer(5, self.receiveMessage()).start()

    @cherrypy.expose # once frontend has been built, don't expose this. we don't want people calling this and posing as us
    def sendMessage(self, message, destination, stamp=int(time.time())):
        # look up the 'destination' user in database and retrieve his corresponding ip address and port
        c = sqlite3.connect(DB_STRING)
        cur = c.cursor()
        cur.execute("SELECT ip, port FROM user_string WHERE username=?",
                    [destination])
        conn_tuple = cur.fetchall()
        conn_format = str(conn_tuple).replace("[(u","").replace("u","").replace(")]","").replace("'","")
        ip, port = conn_format.split(', ') # use this in URL formatting

        # message data must be encoded into JSON

        postdata = self.jsonEncode(cherrypy.session['username'], message, destination, stamp)
        print(postdata)
        req = urllib2.Request("http://" + ip + ":" + port + "/receiveMessage",
                             postdata, {'Content-Type': 'application/json'})
        print(req)
        response = urllib2.urlopen(req).read()
        print(response.get_full_url())
        if (response == '0'): # successful
            print "Message sent to server."
        raise cherrypy.HTTPRedirect("/home")

    @cherrypy.expose
    def test(self, destination):
        # look up the 'destination' user in database and retrieve his corresponding ip address and port
        c = sqlite3.connect(DB_STRING)
        cur = c.cursor()
        cur.execute("SELECT ip, port FROM user_string WHERE username=?",
                    [destination])
        conn_tuple = cur.fetchall()
        conn_format = str(conn_tuple).replace("[(u","").replace("u","").replace(")]","").replace("'","")
        ip, port = conn_format.split(', ')
        print(ip)
        print(port)
        return conn_format

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

    def jsonEncode(self, sender, message, destination, stamp):
        output_dict = { "sender": sender, "message": message, "destination": destination, "stamp": stamp}
        data = json.dumps(output_dict)
        return data



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
    cherrypy.engine.subscribe('start',db_management.setup_total_users_table)
    cherrypy.engine.subscribe('stop', db_management.cleanup_users_database)
    cherrypy.engine.subscribe('stop', db_management.cleanup_msg_table)
    cherrypy.engine.subscribe('stop', db_management.cleanup_total_users_table)
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
