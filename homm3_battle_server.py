import argparse
import json
import socketserver
import logging
import sys
import threading
import os
import time
from datetime import datetime
from typing import Dict

logPath = 'logs'
logsFilename = str(datetime.now().date())

BLOCK_LOGIC = True
DEFAULT_LOGIC = False


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{logPath}/{logsFilename}.log"),
        logging.StreamHandler()
    ]
)

# CONSTANTS
COMPUTER = 'LeftUser'
USER = 'RightUser'
TIMEOUT = 0.1


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class hom3instance:
    def __init__(self):
        # server state variables (default)
        self.current_team = None
        self.tcp_responses_counter = 0
        self.last_connection_timestamp = 0
        self.is_service_active = None

        # game state variables
        self.winner = None

        # computer state
        self.is_computer = None
        self.computer_units = None
        self.computer_possible_moves = None

        # human state
        self.is_player = None
        self.player_units = None
        self.player_possible_moves = None

    def get_service_active_state(self) -> bool:
        # show timeout service state response
        current_timestamp = datetime.now().timestamp()
        if (TIMEOUT + self.last_connection_timestamp) - current_timestamp >= 0:
            return True
        else:
            raise Exception('Timeout!! Too slow...')

    def simple_logic(self, request) -> Dict:
        logging.info(f'@@@@ {self.current_team} @@@@')
        self.tcp_responses_counter += 1
        self.last_connection_timestamp = datetime.now().timestamp()
        self.is_service_active = self.get_service_active_state()
        # определяем за кого сейчас определяется действие
        if request['currentSide'] == 0:
            self.current_team = USER
            self.is_computer = False
            self.is_player = True
        if request['currentSide'] == 1:
            self.current_team = COMPUTER
            self.is_computer = True
            self.is_player = False

        # if BLOCK_LOGIC:
        #    time.sleep(60)

        logging.info(f'{request}')
        action = {"type": "4"}
        if len(request["actions"]["possibleAttacks"]) > 0:
            attack = request["actions"]["possibleAttacks"][0]
            action = {
                "type": 1 if attack["shooting"] else 2,
                "targetId": attack["defenderId"],
                "moveToHex": attack["moveToHex"]
            }
        elif len(request["actions"]["possibleMoves"]) > 0:
            action = {
                "type": 0,
                "moveToHex": request["actions"]["possibleMoves"][0]
            }
        logging.info(f'{action}')
        logging.info(f'{self.tcp_responses_counter}')
        logging.info(f'@@@@ {self.last_connection_timestamp} @@@@')
        return action


class HoMM3BattleTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(32000).strip()
        json_data = json.loads(data)
        # TODO: to ML predictions
        try:
            outer_logic = hom3instance()
            action = outer_logic.simple_logic(request=json_data)
        except Exception as ex:
            raise ex
        self.request.sendall(json.dumps(action).encode('ascii'))


class TcpServer:
    def __init__(self):
        self.server = None

    def start_tcp_server(self, host: str, port: int):
        with socketserver.TCPServer((host, port), HoMM3BattleTCPHandler) as self.server:
            try:
                self.server.allow_reuse_address = True
                self.server.serve_forever(poll_interval=0.1)
            except Exception as ex:
                logging.critical(msg=f'Problem: {str(ex)}\nexit')
                sys.exit(1)

    def stop_tcp_server(self):
        self.server.shutdown()
        self.server.server_close()
        print('Server stopped.')


def kill_vcmi():
    os.system('killall vcmiclient')
    print('Vcmi killed.')


def start_homm3_test_battle(headless=False):
    vcmi_client_path_with_args = \
        '/Users/xsa-osx/DEV/cmake/bin/vcmiclient --spectate --spectate-hero-speed 1 \
          --spectate-battle-speed 1 --spectate-skip-battle-result --onlyAI --ai EmptyAI \
           --disable-video --testmap Maps/template-d1.h3m'
    if headless:
        vcmi_client_path_with_args += ' --headless'
    os.system(vcmi_client_path_with_args + ' > /dev/null 2>&1')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', dest='port', default=9999,
                        help='tcp server port', type=int)
    parser.add_argument('--host', dest='host', default='localhost',
                        help='tcp host url')
    args = parser.parse_args()
    logging.info(f'TCPServer start on {args.host}:{args.port}')

    # tcp service start
    tcp_server = TcpServer()
    tcp_thread = threading.Thread(target=tcp_server.start_tcp_server, args=(args.host, args.port))
    tcp_thread.start()

    # test battle start
    # test_game_thread = threading.Thread(target=start_homm3_test_battle)
    start_homm3_test_battle(headless=True)
    print('game done')
    tcp_server.stop_tcp_server()

    sys.exit()
