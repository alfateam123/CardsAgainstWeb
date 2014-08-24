#-*- coding:utf8 -*-

from threading import Thread
from queue import Queue, Empty
import socket
import logging
from time import sleep
import json
from cardsagainstweb.cah import Player

logging.basicConfig(filename="thread_logs.log", level=logging.DEBUG)

class GameState():
  UserInterface = "ui"
  CommunicationThread = "ct" 

  def __init__(self, playername=""):
    self.messages = {"ui": Queue(), "ct": Queue()}
    self.player = Player(playername)

  def add_message(self, json_message, to_whom, blocking=False):
    logging.debug("[GameState.add_message] someone is adding messages for %s", to_whom)
    if (to_whom == self.CommunicationThread):
      json_message["playerkey"] = self.player.name

    self.messages[to_whom].put(json_message, blocking)
    logging.debug("[GameState.add_message] message added! to %s", to_whom)

  def get_message(self, for_whom, blocking=False):
    try:
      logging.debug("[GameState.get_message] %s is retrieving messages!", for_whom)
      return self.messages[for_whom].get(blocking)
    except Empty:
      logging.debug("[GameState.get_message] no messages for %s", for_whom)
      return {}

class UserInterface(Thread):
  def __init__(self, gamestate_obj):
    Thread.__init__(self)
    self.gs = gamestate_obj

  def get_input(self, user_input):
  	self.gs.add_message({"value": user_input}, self.gs.CommunicationThread)

  def connect_to_server(self):
    print("connecting...")
    self.gs.add_message({"action": "connect"}, self.gs.CommunicationThread)
    print("sent data...")
    doc = self.gs.get_message(self.gs.UserInterface, blocking=True)
    print("received response", doc)

  def run(self):
    self.connect_to_server()
    while True:
      doc = self.gs.get_message(self.gs.UserInterface)
      print("userinterface here, got", doc)


class CommunicationThread(Thread):
  def __init__(self, gamestate_obj):
    Thread.__init__(self)
    self.gs = gamestate_obj

  def run(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.server, int(self.port)))
    try:
      while True:
        doc = self.gs.get_message(self.gs.CommunicationThread)
        print("got doc!", doc)
        if doc:
          s.send(bytes(json.dumps(doc), "UTF-8"))
        data = s.recv(1024)
        print( 'Received', repr(data))
        self.gs.add_message(json.loads(str(data, "UTF-8")), self.gs.UserInterface)
    except socket.error as e:
      logging.error("[CommunicationThread.run] error in socket: %s", e)
      s.close()
      