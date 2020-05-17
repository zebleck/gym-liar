import logging
logger = logging.getLogger(__name__)

from gym_liar.cards.Card import Card

import numpy as np
import random

class Agent:

    # ranks: 1(A),2,3,4,5,6,7,8,9,10,11(J),12(Q),13(K)
    # suits: C, D, H, S

    # features:
    # difference in number of aces
    # IsGoodLie
    # IsBadLie
    # IsTrue
    # IsWin

    def __init__(self):
        self.epsilon = 0.1
        self.alpha = 0.8
        self.gamma = 1
        self.call_cheat = 0.4

        # approximate q learning
        self.n_weights = 5
        self.weights = np.zeros(self.n_weights)

    def act(self, actions, observation):
        said = observation[0]
        if said is None:
            if random.random() < self.epsilon:
                    return actions[random.randint(0,len(actions)-1)]
            else:
                Q = []
                for action in actions:
                    Q.append(self.Calc_Q(observation, action))
                selected_action = actions[Q.index(max(Q))]
                return actions[Q.index(max(Q))]
        else:
            if random.random() < self.call_cheat:
                return actions[0]
            else:
                if random.random() < self.epsilon:
                    return actions[random.randint(1,len(actions)-1)]
                else:
                    Q = []
                    for action in actions[1:]:
                        Q.append(self.Calc_Q(observation, action))
                    selected_action = actions[Q.index(max(Q))+1]
                    return actions[Q.index(max(Q))+1]
                

    def Update_Q(self, old_observation, observation, action):
        Q_t0 = self.Calc_Q(old_observation, action)
        Q_t1 = self.Calc_Q(observation, action)
        features = self.features(old_observation, action)
        reward = len(old_observation[2]) - len(observation[2])
        correction = (reward + self.gamma * Q_t1) - Q_t0

        ''' Debugging '''
        if features[4] is 1:
            print('Reward:',reward)
            print('Q_t1:',Q_t1)
            print('Q_t0:',Q_t0)
            print(features)
            print('----')
        for i in range(len(self.weights)):
            self.weights[i] = self.weights[i] + self.alpha * correction * features[i]

    def features(self, observation, action):
        said = observation[0]
        hand = observation[2]
        hand_ranks = [card.rank for card in hand]

        future_ranks = hand_ranks.copy()
        if 1 in future_ranks:
            future_ranks.remove(1)
        d_aces = hand_ranks.count(1)-future_ranks.count(1)

        if said is None:
            IsGoodLie = (action[0] is not action[1].rank and said in hand_ranks)
            IsBadLie = (action[0] is not action[1].rank and said not in hand_ranks)
            IsTrue = (action[0] is action[1].rank)
            IsWin = (action[0] is action[1].rank and len(hand) is 1)
        else:
            if type(action) is tuple:
                action = action[1]
            IsGoodLie = (said is not action.rank and said in hand_ranks)
            IsBadLie = (said is not action.rank and said not in hand_ranks)
            IsTrue = (said is action.rank)
            IsWin = (said is action.rank and len(hand) is 1)
        return np.array([d_aces, IsGoodLie, IsBadLie, IsTrue, IsWin])

    def Calc_Q(self, observation, action):
        return np.sum(self.weights * self.features(observation, action))
