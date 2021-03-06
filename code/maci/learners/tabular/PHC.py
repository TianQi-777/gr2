from builtins import *

import random
import sys
import os
import math
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from functools import partial

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from .base_tabular_learner import Agent, StationaryAgent
import importlib
import maci.utils as utils

from copy import deepcopy
from .Q import QAgent
from .base_tabular_learner import StationaryAgent



class PHCAgent(QAgent):
    def __init__(self, id_, action_num, env, delta=0.02, **kwargs):
        super().__init__(id_, action_num, env, **kwargs)
        self.name = 'phc'
        self.delta = delta
        self.pi_history = [deepcopy(self.pi)]

    def update_policy(self, s, a, game):
        delta = self.delta
        if a == np.argmax(self.Q[s]):
            self.pi[s][a] += delta
        else:
            self.pi[s][a] -= delta / (self.action_num - 1)
        StationaryAgent.normalize(self.pi[s])
        self.pi_history.append(deepcopy(self.pi))


class WoLFPHCAgent(PHCAgent):
    def __init__(self, _id, action_num, env, delta1=0.001, delta2=0.002, **kwargs):
        super().__init__(_id, action_num, env, **kwargs)
        self.name = 'wolf'
        self.delta1 = delta1
        self.delta2 = delta2
        self.pi_ = defaultdict(partial(np.random.dirichlet, [1.0] * self.action_num))
        self.count_pi = defaultdict(int)

    def done(self, env):
        self.pi_.clear()
        self.count_pi.clear()
        super().done(env)

    def update_policy(self, s, a, env):
        self.count_pi[s] += 1
        self.pi_[s] += (self.pi[s] - self.pi_[s]) / self.count_pi[s]
        self.delta = self.delta1 \
            if np.dot(self.pi[s], self.Q[s]) \
               > np.dot(self.pi_[s], self.Q[s]) \
            else self.delta2
        super().update_policy(s, a, env)
