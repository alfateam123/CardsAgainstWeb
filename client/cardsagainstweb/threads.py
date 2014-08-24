#-*- coding:utf8 -*-

from threading import Thread
from queue import Queue, Empty
import socket
import logging
from time import sleep
import json
from cardsagainstweb.cah import Player
import sys

logging.basicConfig(filename="thread_logs.log", level=logging.DEBUG)

class GameState():
  UserInterface = "ui"
  CommunicationThread = "ct"
  GameState = "gs"

  def __init__(self):
    self.messages = self._init_queues()
    self.player = None
    self.black_card = ""

  def _init_queues(self):
    return {
    self.UserInterface : Queue(),
    self.CommunicationThread : Queue(),
    self.GameState : Queue()
    }

  def add_message(self, json_message, to_whom, blocking=False):
    logging.debug("[GameState.add_message] someone is adding messages for %s", to_whom)
    if to_whom == self.GameState: #it's operational!
      self.__getattribute__(json_message["action"])(json_message)
    else:
      self.messages[to_whom].put(json_message, blocking)
    logging.debug("[GameState.add_message] message added! to %s", to_whom)

  def get_message(self, for_whom, blocking=False):
    try:
      logging.debug("[GameState.get_message] %s is retrieving messages!", for_whom)
      return self.messages[for_whom].get(blocking)
    except Empty:
      logging.debug("[GameState.get_message] no messages for %s", for_whom)
      return {}

  def connect_request(self, message):
    """ from user interface """
    self.player = Player(message["playername"], is_our_player=True)
    self.add_message({"playerkey": self.player.name, "action": "connect"},
                   to_whom=self.CommunicationThread)

  def connect(self, message):
    """ from server """
    if doc["action"] == "connect":
      return (doc["value"] == "accepted", doc["value"])
    else: raise ValueError("[GameState.connect] action %s should not come now!"%doc["action"])
 
  def disconnect_request(self, message):
    """ from user interface """
    self.add_message({"playerkey": self.player.name, "action": "disconnect"},
                      self.CommunicationThread)

  def disconnect(self, message):
    self.add_message({"event": "disconnect", "value": doc["value"]})

  def disconnect_notice(self, message):
    """handled automatically, from server """
    self.add_message({"event": "disconnection_notice", "args": {"player": message["value"]}},
       to_whom=self.UserInterface)

  def start_match(self, message):
    """ from user interface """
    self.add_message({"playerkey": self.player.name, "action":"ready", "value":True},
                     self.CommunicationThread)
    doc = self.get_message(self.GameState, blocking=True)
    if doc["action"] == "ready":
      return (doc["value"] == "accepted_not_ready", doc["value"])
    else: raise ValueError("[GameState.start_match] action %s should not come now!"%doc["action"])

  def card_distribution(self, message):
    """ from server """
    new_cards = message["cards"]
    for card in new_cards: self.player.add_card(card)
    self.add_message({"playerkey": self.player.name, "action": "card_distributed", "value":"success"},
                     self.CommunicationThread)

  def turn_start(self, message):
    """ from server """
    self.add_message({"playerkey": self.player.name, "action": "turn_start", "value":"ready"},
                     self.CommunicationThread)

  def black_card(self, message):
    """ from server """
    self.black_card = message["value"]
    self.add_message({"event": "black_card", "args": {"value": message["value"]}})

  def play_card(self, message):
    """ from user interface """
    card_index = message["args"]["card_index"]
    self.add_message({"playerkey": self.player.name,
                      "action": "play_card",
                      "value":self.player.see_card_at(card_index)
                    }, self.CommunicationThread)
    

  def card_played(self, message):
    """ from server, after userinterface.play_card """
    if "cards_remaining_to_play" in response:
      card_index = self.player.cards.find(message["value"])
      self.player.draw_card(card_index)
      self.add_message({"event": "card_drawn", "success": True, "card_index": card_index},
        self.UserInterface)
    else:
      self.add_message({"event": "card_drawn", "success": False, "error": message["error"]},
        self.UserInterface)

  def card_draw(self, message):
    """ from user interface """
    self.add_message({"playerkey": self.player.name,
                      "action": "card_draw"
                    }, self.CommunicationThread)

  def card_drawn(self, message):
    """ from server """
    self.player.add_card(message["value"])
    self.add_message({"event": "card_drawn"}, self.UserInterface)

  def vote(self, message):
    """ from server """
    other_cards = message["possible_votes"]
    self.add_message({"event": "vote_request", "cards": other_cards},
                    self.UserInterface)

  def vote_response(self, message):
    """ from user interface, after a server.vote request """
    self.add_message({"playerkey": "vote",
                      "value": ui_response["chosen_player"] 
                    }, self.CommunicationThread)

  def turn_end(self, message):
    """ from server """
    self.add_message(message, self.UserInterface)

  def match_end(self, message):
    """ from server """
    self.add_message(message, self.UserInterface)
    self.add_message({"playerkey": "nick",
                      "action": "match_end",
                      "value": "accepted"
                    }, self.CommunicationThread)


class CommunicationThread(Thread):
  """
  this class is for sending/receiving ONLY.
  """
  def __init__(self, gamestate_obj):
    Thread.__init__(self)
    self.gs = gamestate_obj
    self.s = None

  def close_connection(self):
    self.s.close()

  def run(self):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.connect((self.server, int(self.port)))
    try:
      while True:
        doc = self.gs.get_message(self.gs.CommunicationThread)
        print("got doc!", doc)
        if doc:
          self.s.send(bytes(json.dumps(doc), "UTF-8"))
        data = self.s.recv(1024)
        print( 'Received', repr(data))
        self.gs.add_message(json.loads(str(data, "UTF-8")), self.gs.GameState)
    except socket.error as e:
      logging.error("[CommunicationThread.run] error in socket: %s", e)
    self.close_connection()

class UserInterface(Thread):
  def __init__(self, gamestate_obj):
    Thread.__init__(self)
    self.gs = gamestate_obj

  def run(self):
    self.gs.add_message({"action": "connect_request", "playername": "alfa"}, self.gs.GameState)
    doc = self.gs.get_message(self.gs.UserInterface, blocking=True)
    print(doc)
    while True:
      #starting the match!
      self.gs.add_message({
        "action": "card_draw"
        }, self.gs.GameState)



      