import json
import json
import logging
import multiprocessing
import sys
import threading
import time
from datetime import datetime
from socket import socket

from gym import Env

from libs.battle_state import MlService
from libs.common import (kill_vcmi,
                         start_vcmi_test_battle, configure_tcp_socket)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/{str(datetime.now().date())}.log"),
    ]
)

###### OPTIONS ######
CONNECTION_TIMEOUT = 250
CREATION_TIMEOUT = 5
DEFAULT_VCMI_RESET_DEMO_WAITS = 3
DEFAULT_VCMI_RESET_TRAIN_WAITS = 1

LOG_CONNECTION = False
LOG_INFO = False
LOG_WARNING = False
#####################

###### ENV GLOBAL VARIABLES ####
# TODO: to class please
request = None
server_last_packet_time = None
client_start_timestamp = datetime.now().timestamp()
ml_service_socket: socket
#########################

class HoMM3Battle(Env):

    def __init__(self, headless):
        self.homm3_game = None
        self.steps = 0
        # TODO: fix need drop MLServices in reset
        self.instance_state: MlService = MlService()

        if LOG_INFO:
            logging.info('Проверьте включен ли BattleML в настройках vcmilauncher')
        self.server_last_packet_time = None
        self.isHeadless = headless

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
            time.sleep(DEFAULT_VCMI_RESET_TRAIN_WAITS)
        else:
            time.sleep(DEFAULT_VCMI_RESET_DEMO_WAITS)
        self.start_vcmi_threaded()

        # state
        self.steps = 0
        self.instance_state.reset()

        return self.steps

    def tcp_service(self):
        global ml_service_socket
        ml_service_socket = configure_tcp_socket()

    def step(self, action) -> (int, int, bool, dict):
        # wait from environment and make action
        # ждёт запроса от среды о отдаёт действие
        done = False
        global request, connection, ml_service_socket

        is_waiting_response = True
        while is_waiting_response:
            if LOG_WARNING:
                logging.warning("Waiting socket connection...")
            connection, address = ml_service_socket.accept()
            if LOG_INFO:
                logging.info(
                    "new connection from {address}".format(address=address))
            data = connection.recv(32000)
            self.server_last_packet_time = datetime.now().timestamp()
            json_data = json.loads(data)
            request = json_data
            self.instance_state.update(request=json_data)
            is_waiting_response = False

        # TODO: replace fake with minimization for army here
        # TODO: here need to get equivalent last state with current
        # TODO: if step success reward++ else nothing bad

        # simple example
        target_varible: int = 0
        # TODO: fix defect export prediction to Keras
        # TODO: fix fake logic in method
        jaction = self.instance_state.make_prediction(request, target_varible, action)

        # TODO: and setup army's count reward policy
        reward = 0
        if self.instance_state.right_army_count[0] > self.instance_state.right_army_count[1]:
            if self.instance_state.right_army_count[0] != -1 and self.instance_state.right_army_count[1] != -1:
                reward = self.instance_state.right_army_count[0] - self.instance_state.right_army_count[1]

        # get game state done
        if self.instance_state.game_end:
            reward = 1
            done = True
            self.instance_state.reset()


        else:
            # send to vcmi battle ml service
            if LOG_INFO:
                logging.info(f'>>> {self.instance_state.current_team} >>>')
                logging.info(jaction)

            connection.send(json.dumps(jaction).encode('ascii'))
            if LOG_INFO:
                logging.log(logging.INFO, f'send to battle-ml: {jaction}')

            reward = reward
            connection = connection.close()
            request = None
            done = False

        # info
        info = dict()
        self.steps += 1

        return self.steps, reward, done, info

    def hard_reset(self):
        global server_last_packet_time
        server_last_packet_time = datetime.now().timestamp()
        if LOG_WARNING:
            logging.warning('Service not respond.')
        self.kill()
        self.start_vcmi_threaded()

    def kill(self):
        kill_vcmi()

    def render(self, **kwargs):
        if self.isHeadless:
            return
        # TODO: maybe simple update screenshot and show it???
        # TODO: see at base class
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