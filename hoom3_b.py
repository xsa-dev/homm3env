import argparse
import json
import logging
import multiprocessing
import random
import socket
import sys
import threading
import time
from datetime import datetime, timedelta

from gym import Env

from libs.common import (check_client_started, check_connection, kill_vcmi,
                         start_vcmi_test_battle)
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
isHeadless = False
states = 3
CONNECTION_TIMEOUT = 5
CREATION_TIMEOUT = 5
EPISODES = 2
#####################

###### ENV VARIABLES ######
# TODO: to class please
conn = None
request = None
server_last_packet_time = None
client_start_timestamp = datetime.now().timestamp()
client_started = False
#####################

class HoMM3_B(Env):

    def __init__(self):
        self.state = None
        self.instance_state: ml_service = ml_service()
        logging.info('Проверьте включен ли BattleML в настройках vcmilauncher')

    def tcp_service(self):
        # Задаем адрес сервера
        SERVER_ADDRESS = ('localhost', 9999)

        # Настраиваем сокет
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Помечаем чтобы менй пустил дальше
        self.server = True

        server_socket.bind(SERVER_ADDRESS)
        server_socket.listen(1)
        logging.info('Simple Tcp Server is running. 2')

        # Слушаем запросы
        while self.server:
            global conn
            global request
            global server_last_packet_time
            connection, address = server_socket.accept()
            logging.info(
                "new connection from {address}".format(address=address))
            data = connection.recv(32000)
            # фиксируем последнее обращение
            server_last_packet_time = datetime.now().timestamp()
            # to processing logic
            json_data = json.loads(data)

            # TODO: this is state for one agent or multy agents envs
            self.instance_state.update(request=json_data)

            request = json_data
            conn = connection
            logging.info(connection)

    def step(self, action):
        # wait from environment and make action
        # ждёт запроса от среды о отдаёт действие
        global request
        global conn
        if request is None or conn is None:
            # continue
            # ждёт пока появиться подключение
            # никаких поощрений или штрафов
            self.state = self.state
            reward = 0
            done = False
            info = {}
            return self.state, reward, done, info

        # logging выбора значений
        target_varible: int = 0
        jaction = self.instance_state.prediction(request, target_varible)
        logging.info(f'>>> {self.instance_state.current_team} >>>')
        logging.info(jaction)

        # waiting for new connection
        # send to vcmi battle ml service
        # TODO: minor fix always open vcmiclient port
        # TODO: refactor please
        conn.send(json.dumps(jaction).encode('ascii'))
        conn.close()
        conn = None
        request = None

        # TODO: if step success reward++ else reward
        reward = 1
        done = False

        # TODO: minimization for army here
        self.state -= 1
        if self.state <= 0:
            done = True

        # info
        info = dict()

        return self.state, reward, done, info

    def reset(self):
        if not hasattr(self, 'simple_service'):
            self.simple_service = threading.Thread(
                target=self.tcp_service,
                daemon=True
            )
            self.simple_service.start()

        # vcmi
        kill_vcmi()
        if isHeadless:
            time.sleep(5)
        else:
            time.sleep(2)

        self.start_vcmi_threaded()

        # state
        self.state = states

        return self.state

    def render(self):
        pass

    def start_vcmi_threaded(self):
        self.homm3_game = multiprocessing.Process(
            target=start_vcmi_test_battle,
            args=[isHeadless],
            name='vcmi',
            daemon=True
        )
        self.homm3_game.start()

    def actions(self) -> list:
        return [1, 2, 3, 4]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', dest='port', default=9999,
                        help='tcp server port', type=int)
    parser.add_argument('--host', dest='host', default='localhost',
                        help='tcp host url')
    args = parser.parse_args()

    # ENV test
    env = HoMM3_B()

    for episode in range(1, EPISODES + 1):
        # reset сервер и vcmi
        state = env.reset()
        done = False
        score = 0
        # пока игра не закончена
        while not done:
            # ждем создания клиент
            # if not check_client_started():
            #    continue            # ждем включения  tcp сервиса
            # if check_connection(env, conn, server_last_packet_time, CONNECTION_TIMEOUT):
            #    continue

            if conn is None:
                if server_last_packet_time is not None:
                    if datetime.now().timestamp() - server_last_packet_time > 20.0:
                        server_last_packet_time = datetime.now().timestamp()
                        logging.warning('Service not respond.')
                        kill_vcmi()
                        env.start_vcmi_threaded()
                continue

            # выполняем
            env.render()
            # выполнем выбор действия
            action = random.choice(env.actions())
            # получаем состояние, награду, признак завершения, информацию
            n_state, reward, done, info = env.step(action)
            # увеличиванием награду
            score += reward
            logging.info('Step: {} Score: {} Reward: {} Action: {} Done: {} Info: {}'.format(
                n_state, score, reward, action, done, info))

        logging.info('Episode:{} Score:{}'.format(episode, score))
