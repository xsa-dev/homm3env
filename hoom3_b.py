import time

import sys

import argparse
import json
import logging
import random
import threading
import multiprocessing
from datetime import datetime
import socket
from gym import Env
import os

from libs.common import start_vcmi_test_battle, kill_vcmi

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/{str(datetime.now().date())}.log"),
    ]
)

conn = None
request = None
server_last_packet_time = None


class HoMM3_B(Env):

    def __init__(self):
        logging.info('Проверьте включен ли BattleML в настройках vcmilauncher')
        pass

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
        logging.info('Simple Tcp Server is running.')

        # Слушаем запросы
        while self.server:
            global conn
            global request
            global server_last_packet_time
            connection, address = server_socket.accept()
            logging.info("new connection from {address}".format(address=address))
            data = connection.recv(32000)
            # фиксируем последнее обращение
            server_last_packet_time = datetime.now().timestamp()
            # to processing logic
            json_data = json.loads(data)
            request = json_data
            conn = connection
            print(connection)

    def step(self, action):
        # ждёт запроса от среды о отдаёт действие
        global request
        global conn
        if request is None or conn is None:
            # ждёт пока появиться подключение
            # никаких поощрений или штрафов
            self.state = self.state
            reward = 0
            done = False
            info = {}
            return self.state, reward, done, info

        print(self.state)
        rand_int: int = 0

        logging.info(f'{action}')
        jaction = {"type": f"{action}"}

        if len(request["actions"]["possibleAttacks"]) > 0:
            rand_int = random.randint(0, len(request['actions']['possibleAttacks']))

            attack = request["actions"]["possibleAttacks"][0]
            jaction = {
                "type": 1 if attack["shooting"] else 2,
                "targetId": attack["defenderId"],
                "moveToHex": attack["moveToHex"]
            }
        elif len(request["actions"]["possibleMoves"]) > 0:
            rand_int = random.randint(0, len(request["actions"]["possibleMoves"]))

            jaction = {
                "type": 0,  # TODO: testing
                "moveToHex": request["actions"]["possibleMoves"][0]  # TODO testing
            }
        logging.info(f'{request}')
        logging.info(f'{jaction}')

        # to vcmi
        conn.send(json.dumps(jaction).encode('ascii'))
        # TODO: minor fix always open vcmiclient port
        conn.close()
        conn = None
        request = None

        #
        reward = 1
        done = False
        self.state -= 1
        if self.state <= 0:
            done = True
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
        time.sleep(5)
        self.start_vcmi_thred()

        # state
        self.state = 5

    def render(self):
        pass

    def start_vcmi_thred(self):
        self.homm3_game = multiprocessing.Process(
            target=start_vcmi_test_battle,
            args=[True],
            name='vcmi',
            daemon=True
        )
        self.homm3_game.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', dest='port', default=9999,
                        help='tcp server port', type=int)
    parser.add_argument('--host', dest='host', default='localhost',
                        help='tcp host url')
    args = parser.parse_args()

    env = HoMM3_B()

    # env.test_game_thread.start()
    # env.test_game_thread.join()
    # logging.info('Game done.')

    episodes = 10
    for episode in range(1, episodes + 1):
        # reset сервер и vcmi
        state = env.reset()

        done = False
        score = 0

        # пока игра не закончена
        while not done:
            # ждем включения tcp сервиса
            if conn is None:
                if server_last_packet_time is not None:
                    if datetime.now().timestamp() - server_last_packet_time > 30.0:
                        server_last_packet_time = datetime.now().timestamp()
                        logging.warning('Service not respond.')
                        kill_vcmi()
                        env.start_vcmi_thred()
                continue
            # выполняем
            env.render()
            # выполнем выбор действия
            action = random.choice([1, 2, 3, 4])
            # получаем состояние, награду, признак завершения, информацию
            n_state, reward, done, info = env.step(action)
            # увеличиванием награду
            score += reward

        print('Episode:{} Score:{}'.format(episode, score))
    kill_vcmi()
