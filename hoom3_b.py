import json

import sys

import logging

import time

import threading

import random
from gym import Env
import argparse

from libs.common import start_vcmi_test_battle
from libs.tcpserver import TcpServer
from datetime import datetime
from libs.homm3_state import hom3instance

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/{str(datetime.now().date())}.log"),
        logging.StreamHandler()
    ]
)

conn = None
request = None


class HoMM3_B(Env):
    def function(self):
        import socket
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
            connection, address = server_socket.accept()
            logging.info("new connection from {address}".format(address=address))
            data = connection.recv(32000)
            # to processing logic
            json_data = json.loads(data)
            request = json_data
            conn = connection

    def __init__(self):
        self.simple_service = threading.Thread(
            target=self.function,
            daemon=True
        )
        self.simple_service.start()

        self.state = 5
        self.test_game_thread = threading.Thread(
            target=start_vcmi_test_battle,
            args=[False],
            name='vcmi',
            daemon=True
        )
        self.test_game_thread.start()

    def step(self, action):
        # ждёт запроса от среды о отдаёт действие
        global request
        global conn
        if request is None or conn is None:
            self.state = 0
            reward = 0
            done = False
            info = {}
            return self.state, reward, done, info

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
            done = False
        info = dict()

        return self.state, reward, done, info

    def render(self):
        pass

    def reset(self):
        self.state = 0
        self.test_game_thread.start()
        pass


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
        # state = env.reset()

        done = False
        score = 0

        # пока игра не закончена
        while not done:
            if conn is None:
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
        env.test_game_thread.join()
    pass
