import argparse
import json
import socketserver
import logging
import sys
import threading
import os

from datetime import datetime
from typing import Dict

logPath = 'logs'
logsFilename = str(datetime.now().date())

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{logPath}/{logsFilename}.log"),
        logging.StreamHandler()
    ]
)

logging.info('info')


def simple_logic(request) -> Dict:
    # выпиливание простейшего ии от nullkiller
    # type: move = 0, shot = 1, mellee = 2, wait = 3, defence = 4
    # targetId: number, required for shot and mellee
    # moveToHex: number of battlefield hex, required for move, mellee

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
    return action


class HoMM3BattleTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(32000).strip()
        json_data = json.loads(data)
        logging.info(f'{json_data}')
        # TODO: to ML predictions
        action = simple_logic(json_data)
        logging.info(f'{action}')
        self.request.sendall(json.dumps(action).encode('ascii'))


class TcpServer:
    def __init__(self):
        self.server = None

    def start_tcp_server(self, host: str, port: int):
        self.port = port
        with socketserver.TCPServer((host, port), HoMM3BattleTCPHandler) as self.server:
            try:
                self.server.allow_reuse_address = True
                self.server.serve_forever(poll_interval=0.1)
            except Exception as ex:
                pass
                logging.critical(msg=f'Problem: {str(ex)}\nexit')

    def stop_tcp_server(self):
        self.server.shutdown()
        self.server.server_close()
        print('Server stopped.')


def start_homm3_test_battle():
    vcmi_client_path_with_args = \
        '/Users/xsa-osx/DEV/cmake/bin/vcmiclient --spectate --spectate-hero-speed 1 \
          --spectate-battle-speed 1 --spectate-skip-battle-result --onlyAI --ai EmptyAI \
           --disable-video --testmap "Maps/template-d1.h3m" --headless'
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
    start_homm3_test_battle()
    print('game done')
    tcp_server.stop_tcp_server()

    sys.exit()
