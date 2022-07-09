# 

from gym import Env
from gym.spaces import Discrete, Box
from numpy import np

class HoMM3_B(Env):
    def __init__(self):
      self.action_space = Discrete(4)
      self.observation_space = Box(low=np.array([0]), high = np.array([100]))
      self.state = 10 # opponents army
      self.shower_length = 100 # game turn

