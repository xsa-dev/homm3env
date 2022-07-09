import time

import numpy as np

import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym.wrappers import Monitor  # to video record

import os
import homm3_battle_server as homm3api

# CONSTANTS
GAME = None
BUILD_FOLDER_PATH = r"/home/xsa/DEV/xsa-dev/grpc/examples/cpp/vcmi/cmake/build"
EXE_PATH_CLIENT = r"bin/vcmiclient"
EXE_PATH_SERVER = r"bin/vcmiserver"
EXE_PATH_SERVICE = "greeter_async_server"


class Homm3Env(gym.Env):
    metadata = {'render.modes': ['headless',
                                 'human',
                                 'rgb_array']}

    def start_test_battle(self):
        vcmi_client_path_with_args = \
            '/Users/xsa-osx/DEV/cmake/bin/vcmiclient --spectate --spectate-hero-speed 1 \
              --spectate-battle-speed 1 --spectate-skip-battle-result --onlyAI --ai EmptyAI \
               --disable-video --testmap "Maps/template-d1.h3m" --headless'
        os.system(vcmi_client_path_with_args + ' > /dev/null 2>&1')

    def __init__(self):
        self.server = homm3api.TcpHandler()
        self.action_space = spaces.Discrete(4)
        self.reset()
        self.STEP_LIMIT = 1000
        self.sleep = 0
        # start cpp env

        # run it:
        # server only
        self.server.start_ai_server()
        # server and client locally
        # server and client host, client join
        # many client on one host
        # finish

    def step(self, action):
        scoreholder = self.score
        reward = 0
        self.direction = Homm3Env.scan_direction(action, self.direction)
        self.hero_pos = Homm3Env.move(self.direction, self.hero_pos)
        reward = self.farm_handler()
        self.update_game_state()
        reward, done = self.game_over(reward)
        state = self.get_state_from_service()
        info = {"score": self.score}
        self.steps += 1
        time.sleep(self.sleep)
        return state, reward, done, info

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

    def get_state_from_service(self):
        # or use
        state = None
        return state

    def game_over(self, reward):
        if self.hero_pos[0] < 0 or self.hero_pos[0] > self.frame_size_x - 10:
            return -1, True
        if self.hero_pos[1] < 0 or self.hero_pos[1] > self.frame_size_y - 10:
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
