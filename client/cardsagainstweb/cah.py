#-*- coding:utf8 -*-

import json
from random import randint

class Player(object):
  def __init__(self, name=None, is_our_player=False):
    self.name = name or self.random_name()
    self.cards = list()  
    self.is_our_player = is_our_player

  def random_name(self):
    return "".join(chr(97+randint(0,26)) for i in range(7))

  def draw_card(self, card_index):
    if not self.is_our_player:
      raise AttributeError("you can't call Player.draw_card on a player you don't control!")
    self.cards[-1], self.cards[card_index] = self.cards[card_index], self.cards[-1]
    self.cards.pop()

  def add_card(self, card_text):
    if not self.is_our_player:
      raise AttributeError("you can't call Player.add_card on a player you don't control!")
    self.cards.append(card_text)

class Game(object):
  def __init__(self):
    self.black_card = ""
    self.player = None



  


