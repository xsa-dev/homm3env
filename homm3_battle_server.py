import time

import argparse
import logging
import sys
import threading
from datetime import datetime

from libs.common import start_vcmi_test_battle
from libs.tcpserver import TcpServer

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/{str(datetime.now().date())}.log"),
        logging.StreamHandler()
    ]
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', dest='port', default=9999,
                        help='tcp server port', type=int)
    parser.add_argument('--host', dest='host', default='localhost',
                        help='tcp host url')
    args = parser.parse_args()

    # tcp service start
    tcp_server = TcpServer()
    tcp_thread = threading.Thread(
        target=tcp_server.start_simple_tcp_server,
        args=(args.host, args.port),
        name='transport',
        daemon=True
    )
    tcp_thread.start()

    time.sleep(5)
    if tcp_server.server is None:
        logging.info('Server not started.')
        sys.exit()
    else:
        logging.info('Server started.')

    # test battle start
    test_game_thread = threading.Thread(
        target=start_vcmi_test_battle,
        args=[True],
        name='vcmi'
    )
    test_game_thread.start()
    test_game_thread.join()
    logging.info('Game done.')

    tcp_server.stop_tcp_server(method='Simple')
    sys.exit()
