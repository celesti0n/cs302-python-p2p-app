import time
import datetime
# this file holds all the functions which helps convert standard epoch time form into human-readable time signatures.

def epochFormat(timeStamp):  # helper function for detailed date timestamp
    return datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S').encode('ascii', 'ignore')

def timeSinceMessage(timeStamp):  # helper function for timestamp in relation to current time
    timeSince = time.time() - timeStamp
    units = ''
    if timeSince < 60:
        timeSince = int(round(timeSince))
        units = ' second(s) ago'
    elif timeSince >= 60 and timeSince < 3600:
        timeSince = int(round(timeSince / 60))
        units = ' minute(s) ago'
    elif timeSince >= 3600 and timeSince < 86400:
        timeSince = int(round(timeSince / 3600))
        units = ' hour(s) ago'
    elif timeSince >= 86400:
        timeSince = int(round(timeSince / 86400))
        units = ' day(s) ago'
    return str(timeSince) + units
