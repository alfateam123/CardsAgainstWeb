#-*- coding:utf8 -*-

import json
from random import randint

class Player(object):
  def __init__(self, name=None):
    self.name = name or self.random_name()
    self.cards = list()  

  def random_name(self):
    return "".join(chr(97+randint(0,26)) for i in range(7))

  def draw_card(self, card_index):
    self.cards[-1], self.cards[card_index] = self.cards[card_index], self.cards[-1]
    self.cards.pop()

  def add_card(self, card_text):
    self.cards.append(card_text)

class GameState(object):
  def __init__(self):
    self.black_card = ""
    self.players = list()

  def add_player(self, new_player):
    self.players.append(new_player)

  def remove_player(self, old_player):
    self.players.remove(old_player)

  


