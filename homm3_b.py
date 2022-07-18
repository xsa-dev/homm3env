import argparse
from http.client import OK
import json
import logging
import multiprocessing
from multiprocessing.connection import wait
import random

import sys
import threading
import time
from datetime import datetime, timedelta

from gym import Env

from libs.common import (check_connection, kill_vcmi,
                         start_vcmi_test_battle, configure_tcp_socket, callback_vcmi)

from libs.battle_state import MlService


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/{str(datetime.now().date())}.log"),
    ]
)

###### OPTIONS ######
states = 100
CONNECTION_TIMEOUT = 250
CREATION_TIMEOUT = 5
DEFAULT_VCMI_DEMO_WAITS = 3
DEFAULT_VCMI_TRAIN_WAITS = 1

LOG_CONNECTION = False
LOG_INFO = False
LOG_WARNING = False
#####################

###### ENV VARIABLES ####
# TODO: to class please
conn = None
request = None
server_last_packet_time = None
client_start_timestamp = datetime.now().timestamp()


#########################

class HoMM3_B(Env):

    def __init__(self, headless):
        self.homm3_game = None
        self.state = None
        # TODO: fix need drop MLServices in reset
        self.instance_state: MlService = MlService()

        if LOG_INFO:
            logging.info('Проверьте включен ли BattleML в настройках vcmilauncher')
        self.server_last_packet_time = None
        self.isHeadless = headless

    def tcp_service(self):
        global conn
        global request
        global server_last_packet_time

        # create socket with default params
        server_socket = configure_tcp_socket()

        # Слушаем запросы
        while True:
            connection, address = server_socket.accept()
            if LOG_INFO:
                logging.info(
                    "new connection from {address}".format(address=address))
            data = connection.recv(32000)
            # фиксируем последнее обращение
            self.server_last_packet_time = datetime.now().timestamp()

            # to processing logic
            json_data = json.loads(data)

            # TODO: this is state for one agent or multy agents envs
            self.instance_state.update(request=json_data)

            # TODO: this is response from server
            request = json_data
            conn = connection

            if LOG_CONNECTION:
                logging.info(connection)

    def reset(self):
        if not hasattr(self, 'simple_service'):
            self.simple_service = threading.Thread(
                target=self.tcp_service,
                daemon=True
            )
            self.simple_service.start()

        # vcmi
        self.kill()
        if self.isHeadless:
            time.sleep(DEFAULT_VCMI_TRAIN_WAITS)
        else:
            time.sleep(DEFAULT_VCMI_DEMO_WAITS)
        self.start_vcmi_threaded()

        # state
        self.state = states
        self.instance_state.reset()

        return self.state

    def callback_vcmi_json(self, jaction):
        # TODO: minor fix always open vcmiclient port
        # TODO: refactor please
        # waiting for new connection
        global conn
        global request
        conn.send(json.dumps(jaction).encode('ascii'))
        if LOG_INFO:
            logging.log(logging.INFO, f'send to battle-ml: {jaction}')
        conn.close()
        conn = None
        request = None

    def step(self, action):
        # wait from environment and make action
        # ждёт запроса от среды о отдаёт действие
        global request
        global conn

        done = False
        # TODO: wait connection or request or engine in separate functions
        wait_counter = 0
        while request is None or conn is None:
            wait_counter += 1
            time.sleep(0.1)
            if wait_counter % 10 == 0:
                logging.log(logging.WARNING, f'Waits backend connection... {wait_counter / 10} sec.')
            if wait_counter > CONNECTION_TIMEOUT:
                raise Exception('Bad tcp connection')

        # logging выбора значений
        target_varible: int = 0
        # TODO: fix defect export prediction to Keras
        jaction = self.instance_state.prediction(request, target_varible)

        # TODO: replace fake with minimization for army here
        # TODO: logic: here need to get equivalent last state with current
        # TODO: if step success reward++ else nothing bad
        self.state -= 1
        if self.state <= 0:
            done = True

        # set army's count logic
        reward = 0
        if self.instance_state.right_army_count[0] > self.instance_state.right_army_count[1]:
            if self.instance_state.right_army_count[0] != -1 and self.instance_state.right_army_count[1] != -1:
                reward = self.instance_state.right_army_count[0] - self.instance_state.right_army_count[1]

        # get game state done
        if self.instance_state.game_end:
            done = True
            self.instance_state.reset()
            reward = 1

        else:
            # send to vcmi battle ml service
            if LOG_INFO:
                logging.info(f'>>> {self.instance_state.current_team} >>>')
                logging.info(jaction)
            self.callback_vcmi_json(jaction)
            reward = reward
            done = False

        # info
        info = dict()

        return self.state, reward, done, info

    def hard_reset(self):
        global server_last_packet_time
        server_last_packet_time = datetime.now().timestamp()
        if LOG_WARNING:
            logging.warning('Service not respond.')
        self.kill()
        self.start_vcmi_threaded()

    def kill(self):
        kill_vcmi()

    def render(self):
        pass

    def start_vcmi_threaded(self):
        self.homm3_game = multiprocessing.Process(
            target=start_vcmi_test_battle,
            args=[self.isHeadless],
            name='vcmi',
            daemon=True
        )
        self.homm3_game.start()

    def actions(self) -> list:
        return [1, 2, 3, 4]
