import os, subprocess, time, signal
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding
import random

from gym_liar.cards.Card import Card
from gym_liar.utils.Utils import pop_slice
from gym_liar.agents.Agent import Agent

import logging
logger = logging.getLogger(__name__)

class LiarEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    # 4 player game popular known as 'Cheat'

    def __init__(self):
        self.n = 52 # cards in deck
        self.n_players = 4 # number of players
        self.starting_player = 0
        self.current_player = 0
        self.said = None

        self.agents = []
        for i in range(self.n_players):
            self.agents.append(Agent())
        
        self.old_observation = [None]*self.n_players # used for reward calculation
        self.old_action = [None]*self.n_players
        self.player_hands = []
        self.pile = []
        self.last_played = []
        
        self.reset()

    def step(self):
        self.old_observation[self.current_player] = self.get_observation(self.current_player)
        action = self.agents[self.current_player].act(self.get_actions(), self.old_observation[self.current_player])
        self.old_action[self.current_player] = action

        # When the player starts a new turn
        if self.said is None:
            self.said = action[0]
            self.pile.extend([action[1]])
            self.player_hands[self.current_player].remove(action[1])
            self.last_played = [action[1]]
            self.current_player = (self.current_player + 1) % self.n_players
        # When the turn is ongoing
        else:
            # bluff is called
            if action is 0:
                
                playerLied = False
                for card in self.last_played:
                    if self.said is not card.rank:
                        playerLied = True
                        break
                previous_player = (self.current_player - 1) % self.n_players
                if playerLied:
                    self.player_hands[previous_player].extend(self.pile)
                    self.check_four_cards(previous_player)

                    # Update Q of previous player
                    self.agents[previous_player].Update_Q(self.old_observation[previous_player], self.get_observation(previous_player), self.old_action[previous_player])
                    self.last_played = []
                    self.pile = []
                    self.said = None
                    if len(self.player_hands[previous_player]) is 0:
                        return True
                else:
                    self.player_hands[self.current_player].extend(self.pile)
                    self.check_four_cards(self.current_player)
                    # Update Q of previous player
                    self.agents[previous_player].Update_Q(self.old_observation[previous_player], self.get_observation(previous_player), self.old_action[previous_player])
                    # Check for win
                    if len(self.player_hands[previous_player]) is 0:
                        self.current_player = (self.current_player + 1) % self.n_players
                        self.last_played = []
                        self.pile = []
                        self.said = None
                        return True
                    if len(self.player_hands[self.current_player]) is 0:
                        self.current_player = (self.current_player + 1) % self.n_players
                        self.last_played = []
                        self.pile = []
                        self.said = None
                        return True

                    self.current_player = (self.current_player + 1) % self.n_players
                    self.last_played = []
                    self.pile = []
                    self.said = None
            # bluff is not called, card gets played
            else:
                self.pile.extend([action])
                self.player_hands[self.current_player].remove(action)
                self.last_played = [action]

                # Update Q of previous player
                previous_player = (self.current_player - 1) % self.n_players
                self.agents[previous_player].Update_Q(self.old_observation[previous_player], self.get_observation(previous_player), self.old_action[previous_player])
                # Check for win
                if len(self.player_hands[previous_player]) is 0:
                    self.current_player = (self.current_player + 1) % self.n_players
                    return True   
                
                self.current_player = (self.current_player + 1) % self.n_players
                
        return False
        #return #ob, reward, episode_over, {}

    def reset(self):
        self.current_player = 0
        self.pile = []
        self.last_played = []

        self.said = None
        self.deck = []
        self.fill_deck()
        random.shuffle(self.deck)

        self.old_observation = [None]*self.n_players
        self.old_action = [None]*self.n_players
        self.player_hands = []
        for i in range(self.n_players):
            self.player_hands.append(pop_slice(self.deck, self.n/self.n_players))
            self.check_four_cards(i)
        
        return self.get_state()

    def render(self, mode='human', close=False):
        print(str(self))

    def  __str__(self):
        string = ''
        string = string + 'Player to move: ' + str(self.current_player) + '\n'
        if self.said is not None:
            string = string + 'Said card: ' + str(Card.rankDict[self.said]) + '\n'
            string = string + 'Last played:' + '\n'
            string = string + '['
            for card in self.last_played:
                string = string + str(card) + ','
            string = string + ']' + '\n'
            string = string + 'Pile:' + '\n'
            string = string + '['
            for card in self.pile:
                string = string + str(card) + ','
            string = string + ']' + '\n'
        for i in range(self.n_players):
            string = string + 'Player {:} ({:} cards):\n'.format(i, len(self.player_hands[i]))
            string = string + '['
            for card in self.player_hands[i]:
                string = string + str(card) + ','
            string = string + ']' + '\n'
        return string

    def fill_deck(self):
        ranks = [i for i in range(1, 14)]
        suits = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    
        for rank in ranks:
            for i in range(4):
                self.deck.append(Card(rank, suits[i]))

    '''
    observation space:
    0 - said
    1 - pile size
    2 - player hand
    3.. - number of cards of other players starting at player thats next
    
    '''
    def get_observation(self, selected_player):
        observation = []
        observation.append(self.said)
        observation.append(len(self.pile))
        observation.append(self.player_hands[selected_player].copy())
        for hand in self.player_hands:
            observation.append(len(hand))
        
        return observation

    '''
    list of actions:

    if said is None:
        [
        [(rank, card)],
        [(rank, card)]
        ]
        array of arrays
        first element contains true moves
        second element contains lying moves
    else:
        0 - turn up last played cards
        card - play card
    '''
    def get_actions(self):
        hand = self.player_hands[self.current_player]
        if self.said is None:
            sorted_options = [[],[]]
            for rank in Card.rankDict.keys():
                # you can only lie aces
                if rank is not 1:
                    for card in hand:
                        if card.rank is rank:
                            sorted_options[0].append((rank, card))
                        else:
                            sorted_options[1].append((rank, card))
            options = [action for sublist in sorted_options for action in sublist]
                    
        else:
            options = [0]
            for card in hand:
                    options.append(card)
                
        return options
        #if not pile:
        #    
        #else:
        #    return [0, self.players[]]

    def get_state(self):
        return self

    def check_four_cards(self, n):
        rank_counts = [0] * 13
        for card in self.player_hands[n]:
            rank_counts[card.rank-1] = rank_counts[card.rank-1] + 1
        self.player_hands[n] = [card for card in self.player_hands[n] if rank_counts[card.rank-1] is not 4]
