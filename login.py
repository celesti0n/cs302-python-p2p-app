import os
import os.path
import sqlite3
import string

import cherrypy
from cherrypy.lib import auth_digest

DB_STRING = "users.db"


class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return file('index.html')

    @cherrypy.expose
    def register(self, username, password, work_id):
        #in the future need to have length checks for params
        with sqlite3.connect(DB_STRING) as c:
            c.execute("INSERT INTO user_string VALUES (?, ?, ?, ?)",
            [cherrypy.session.id, username, password, work_id])
        return open('home.html').read().format(name=username,sid=cherrypy.session.id)


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
        con.execute("CREATE TABLE user_string (session_id, username, password, work_id)")


def cleanup_database():
    """
    Destroy 'user_string' table when server shuts down.
    Maybe take this out later.
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("DROP TABLE user_string")


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
