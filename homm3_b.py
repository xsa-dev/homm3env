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
from libs.homm3_state import ml_service

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/{str(datetime.now().date())}.log"),
    ]
)


###### OPTIONS ######
states = 10
CONNECTION_TIMEOUT = 25
CREATION_TIMEOUT = 5
DEFAULT_VCMI_DEMO_WAITS = 3
DEFAULT_VCMI_TRAIN_WAITS = 1
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
        self.state = None
        self.instance_state: ml_service = ml_service()
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

        return self.state

    def step(self, action):
        # wait from environment and make action
        # ждёт запроса от среды о отдаёт действие
        global request
        global conn

        # TODO: wait connection or request or engine in separate functions
        wait_counter = 0
        while request is None or conn is None:
            wait_counter+=1
            time.sleep(1)
            logging.warn(f'Waits backend connection... {wait_counter} sec.')
            if wait_counter > CONNECTION_TIMEOUT:
                raise Exception('Bad tcp connection')


        # logging выбора значений
        target_varible: int = 0
        jaction = self.instance_state.prediction(request, target_varible)
        logging.info(f'>>> {self.instance_state.current_team} >>>')
        logging.info(jaction)

        # waiting for new connection
        # send to vcmi battle ml service
        # TODO: minor fix always open vcmiclient port        
        # TODO: refactor please
        # callback_vcmi(conn, jaction)
        conn.send(json.dumps(jaction).encode('ascii'))
        conn.close()
        conn = None
        request = None

        # TODO: if step success reward++ else nothing bad
        reward = 1
        done = False

        # TODO: replace fake with minimization for army here
        self.state -= 1
        if self.state <= 0:
            done = True

        # info
        info = dict()

        return self.state, reward, done, info

    def hard_reset(self):
        global server_last_packet_time
        server_last_packet_time = datetime.now().timestamp()
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



