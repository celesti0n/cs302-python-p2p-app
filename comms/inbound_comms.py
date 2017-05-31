import json
import time
import cherrypy
import sqlite3
import threading

DB_STRING = "users.db"
listen_ip = "0.0.0.0" # 127.0.0.1 = localhost (loopback address), use 0.0.0.0 for local machine access
listen_port = 10001

class Comms(object):



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

def setup_msg_table():
    """
    Create the msg table in the database, which stores messages sent to the user
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("CREATE TABLE msg (msg_id INTEGER PRIMARY KEY, sender, msg, stamp)")
        # add public key argument to this later when required

def cleanup_msg_table():
    """
    Destroy 'msg' table when server shuts down.
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("DROP TABLE msg")
