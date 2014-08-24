Requests
========
aka: remember good manners.

Overview
--------

This is the list of messages that can be sent between the threads (or the shared object).
This document will replace protocol_draft.txt

## User Interface -> Game State

* connect_request
```
    { "playername": "winter", "action": "connect_request" }
```
To be sent when connecting to a server. Actually, the server is specified via command line (as --server parameter), so we don't really have to include it in the message.
UI must wait for a (connection event message).

## Game State -> Communication Thread

* connect
```
    { playerkey: "nick", action: "connect" }
```
This is the request the client _actually_ does to the Go server.
A (connect message) will be delivered from Communication Thread

## Communication Thread -> Game State

* connect
```
    { playerkey: "nick", action: "connect", value: "accepted" } 
    { playerkey: "nick", action: "connect", value: "nick already registered" } 
    { playerkey: "nick", action: "connect", value: "generic error" }
```
These are the responses you can expect from the server when you send a (connect message from Game State)

