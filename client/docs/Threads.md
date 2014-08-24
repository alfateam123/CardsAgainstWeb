Threads.py
==========

aka: Spanish Inquisition wants me dead for this

Overview
--------

We have two threads sharing an object

* CommunicationThread (thread)
It's dead simple: it just picks up messages, sends them to the server and gives back responses.

* UserInterface (thread)
It will tell the user the state of the game.

* GameState (shared object)
Store messages, reacts to messages sent to him.