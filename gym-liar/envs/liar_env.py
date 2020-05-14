import os, subprocess, time, signal
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding

import logging
logger = logging.getLogger(__name__)

class LiarEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        print('Initialized.')
        '''self.observation_space = spaces.Box(low=-1, high=1,
                                            shape=(self.env.getStateSize()))
        # Action space omits the Tackle/Catch actions, which are useful on defense
        self.action_space = spaces.Tuple((spaces.Discrete(3),
                                          spaces.Box(low=0, high=100, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1),
                                          spaces.Box(low=0, high=100, shape=1),
                                          spaces.Box(low=-180, high=180, shape=1)))'''

    def step(self, action):
        return None#ob, reward, episode_over, {}

    def reset(self):
        return self.env.getState()

    def render(self, mode='human', close=False):
        print('Hello World!')
