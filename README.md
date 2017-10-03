## COMPSYS302 PROJECT B - mwon724 
> Task: Create a peer-to-peer, login server hybrid web application which serves as a messaging client and social networking tool between other students in the COMPSYS302 class. Data is sent and received purely p2p, but authentication is conducted via a centralised login server. This README includes instructions on how to compile and run my implementation, 'fort secure chat'. 

## How to Run

Make sure you are running Ubuntu and are using Python 2.7.

To begin, download the repository from: https://celestion@bitbucket.org/celestion/uoa-cs302-2017-mwon724.git
Navigate to the branch PROJECT-B-DELIVERABLES and download the latest commit.
In Terminal, navigate to the location of the repository and run python login.py
Observe the IP address and port stated on the third line - 'Engine serving on...'
Enter this address into the browser of your choice to access the client.


## List of Dependencies

Standard Python Libraries, Markdown 2.6.8, CherryPy

Technology stack: HTML, CSS, JQuery, Python, CherryPy

#### Users that have been proven to be able to:
> Send, receive and view messages: mhen418, abha808, hone075, myep112, imar759 
>> Send, receive and view profiles: imar759, mhen418, wgra528, hone075
>>> Send, receive and view files: nmag404, abha808, stoo718, hone075 
>>>> Send and receive status: aalo097, wgra538, hone075 
>>>>> Send and receive formatted messages in Markdown: myep112, abha808, hone075

## List of internal features

- #### User can login and see who is currently online on the network
- #### User can see and edit their own 'profile page', while being able to load other user's profiles
- #### User can send and receive messages and files from someone else currently online
- #### Web application automatically updates content via JQuery for non-obtrusive message refresh
- Localised SQLite database used for data capture and retrieval 
- Embedded media player for video and audio
- Custom statuses - online, away, appear offline
- Local blacklisting of disruptive clients/unwanted users 
- Logs out of server upon automatically an unhandled application exit
- #### Markdown format supported for formatting messages
- Rate limiting API requests to local peer-to-peer node
- Use of multithreading, for regular interaction between client and login server
- Profile pages and messages search via Python SQLite library
- #### Cross-browser support, fluid and minimalistic UI 
- #### Two Factor Authentication enabled for new users

More features to work on:
- Complying with AES, successful inter-app encryption
- Offline messaging support
- Exploring page templating via Jinja2
- Writing unit tests

