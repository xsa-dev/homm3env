import time

import numpy as np

import gym
from gym import error, spaces, utils
from gym.utils import seeding 
from gym.wrappers import Monitor # to video record

GAME = None


class Homm3Env(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space = spaces.Discrete(4)
        self.reset()
        self.STEP_LIMIT = 1000
        self.sleep = 0

    def step(self, action):
        scoreholder = self.score
        reward = 0
        self.direction = Homm3Env.scan_direction(action, self.direction)
        self.hero_pos = Homm3Env.move(self.direction, self.hero_pos)
        reward = self.farm_handler()
        self.update_game_state()
        reward, done = self.game_over(reward)
        img = self.get_image_from_game()
        info = {"score": self.score}
        self.steps += 1
        time.sleep(self.sleep)
        return img, reward, done, info

    @staticmethod
    def scan_direction(action, direction):
        if action == 0 and direction != "DOWN":
            direction = 'UP'
        if action == 1 and direction != "UP":
            direction = 'DOWN'
        if action == 2 and direction != "RIGHT":
            direction = 'LEFT'
        if action == 3 and direction != "LEFT":
            direction = 'RIGHT'
        return direction

    @staticmethod
    def move(direction, hero_pos):
        if direction == 'UP':
            hero_pos[1] -= 10
        if direction == 'DOWN':
            hero_pos[1] += 10
        if direction == 'LEFT':
            hero_pos[0] -= 10
        if direction == 'RIGHT':
            hero_pos[0] += 10
        return hero_pos

    def attack(self):
        return self.hero_pos[0] == self.battle_pos[0] and self.hero_pos[1] == self.battle_pos[1]

    def check_farm_targets(self):
        # return get_window_state_from_server()
        return False

    def farm_handler(self):
        if self.attack():
            self.score += 1
            reward = 1
        else:
            reward = 0

        if not self.monsters_spawn:
            self.battle_pos = self.check_farm_targets()
        self.monsters_spawn = True

        return reward

    def update_game_state(self):
        # return get_game_state_from_server()
        pass

    def get_image_from_game(self):
        # or use
        img = None
        return img

    def game_over(self, reward):
        if self.hero_pos[0] < 0 or self.hero_pos[0] > self.frame_size_x-10:
            return -1, True
        if self.hero_pos[1] < 0 or self.hero_pos[1] > self.frame_size_y-10:
            return -1, True

        if self.steps >= 1000:
            return 0, True

        return reward, False

    def reset(self):
        return True

    def render(self, mode='human'):
        if mode == "human":
            pass

    def close(self):
        pass
