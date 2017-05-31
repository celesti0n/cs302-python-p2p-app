#!/usr/bin/python
""" example.py

    COMPSYS302 - Software Design
    Author: Andrew Chen (andrew.chen@auckland.ac.nz)
    Last Edited: 19/02/2015

    This program uses the CherryPy web server (from www.cherrypy.org).
"""
# Requires:  CherryPy 3.2.2  (www.cherrypy.org)
#            Python  (We use 2.7)

import cherrypy
import sys
import urllib
import urllib2
import time
import login

# The address we listen for connections on
listen_ip = "0.0.0.0"
try:
    listen_port = int(sys.argv[1])
except (IndexError, TypeError):
    listen_port = 1234

class MainApp(object):

    #CherryPy Configuration
    _cp_config = {'tools.encode.on': True,
                  'tools.encode.encoding': 'utf-8',
                 }

    # If they try somewhere we don't know, catch it here and send them to the right place.
    @cherrypy.expose
    def default(self, *args, **kwargs):
        """The default page, given when we don't recognise where the request is for."""
        Page = "I don't know where you're trying to go, so have a 404 Error."
        cherrypy.response.status = 404
        return Page

    # PAGES (which return HTML that can be viewed in browser)
    @cherrypy.expose
    def index(self):
        Page = "Welcome! This is a test website for COMPSYS302!<br/>"
        mfile = open("messages"+str(listen_port)+".txt", "r")
        text = mfile.readlines()
        mfile.close()
        for line in text:
            Page += line+"<br/>"
        Page += '<form accept-charset="utf-8" action="/sendMessage" method="post" enctype="multipart/form-data">'
        Page += '<input type="text" size="100" name="message"/><br/>'
        Page += 'Destination: <input type="text" size="20" name="destination"/>'
        Page += '<input type="submit" value="Send"/></form>'
        return Page

    @cherrypy.expose
    def sum(self, a=0, b=0): #All inputs are strings by default
        output = int(a)+int(b)
        return str(output)

    @cherrypy.expose
    def receiveMessage(self, message, sender=None):
        now = time.strftime("%d-%m-%Y %I:%M %p",time.localtime(float(time.mktime(time.localtime()))))
        mfile = open("messages"+str(listen_port)+".txt", "a")
        mfile.write("["+now+"] Client "+sender+": "+message+"\r\n")
        mfile.close()
        print "Message received from "+sender
        return "Received!"

    @cherrypy.expose
    def sendMessage(self, message, destination):
        postdata = {"message": message, "sender": str(listen_port)}
        dest = "http://127.0.0.1:"+destination+"/receiveMessage"
        fptr = urllib2.urlopen(dest, urllib.urlencode(postdata))
        data = fptr.read()
        fptr.close()
        print "Message sent to server."
        raise cherrypy.HTTPRedirect("/")

def runMainApp():
    # Create an instance of MainApp and tell Cherrypy to send all requests under / to it. (ie all of them)
    cherrypy.tree.mount(MainApp(), "/")

    # Tell Cherrypy to listen for connections on the configured address and port.
    cherrypy.config.update({'server.socket_host': listen_ip,
                            'server.socket_port': listen_port,
                            'engine.autoreload.on': True,
                            'tools.gzip.on' : True,
                            'tools.gzip.mime_types' : ['text/*'],
                           })

    print "========================="
    print "University of Auckland"
    print "COMPSYS302 - Software Design Application"
    print "========================================"

    # Start the web server
    cherrypy.engine.start()

    # And stop doing anything else. Let the web server take over.
    cherrypy.engine.block()

#Run the function to start everything
runMainApp()
