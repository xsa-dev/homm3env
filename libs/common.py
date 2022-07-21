import threading

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

import socket

LOGGING = False


def kill_vcmi():
    os.system("killall -9 vcmiserver")
    os.system("killall -9 vcmiclient")
    if LOGGING:
        logging.info('vcmi killed.')


def start_vcmi_test_battle(headless=False, release=True):
    # build paths
    if release:
        bin_path = '/home/xsa-lin/DEV/build/bin/vcmiclient'
    if not release:
        bin_path = '/home/xsa-lin/DEV/build/bin/vcmiclient'

    # start params
    vcmi_client_path_with_args = \
        f'{bin_path} --spectate --spectate-hero-speed 1 \
          --spectate-battle-speed 1 --spectate-skip-battle-result --onlyAI --ai BattleML \
          --disable-video --testmap Maps/template-d1.h3m'

    # start params append
    if headless:
        vcmi_client_path_with_args += ' --headless'

    # start process
    os.system(vcmi_client_path_with_args + ' > /dev/null 2>&1')
    if LOGGING:
        logging.debug(vcmi_client_path_with_args)
    logging.info('vcmi started.')


def get_thread_by_name(name):
    threads = threading.enumerate()  # Threads list
    for thread in threads:
        if thread.name == name:
            return thread


def check_connection(env, conn, server_last_packet_time, CONNECTION_TIMEOUT) -> bool:
    if conn is None:
        if server_last_packet_time is not None:
            if datetime.now().timestamp() - server_last_packet_time > CONNECTION_TIMEOUT:
                server_last_packet_time = datetime.now().timestamp()
                logging.warning('Service not respond.')
                kill_vcmi()
                env.start_vcmi_thred()
                return False
    return True


def check_client_started() -> bool:
    # todo: make works well
    # if not client_started:
    #     if datetime.now().timestamp() - client_start_timestamp > CREATION_TIMEOUT:
    #         server_last_packet_time = datetime.now().timestamp()
    #         logging.warning('Client not respond.')
    #         kill_vcmi()
    #         env.start_vcmi_thred()
    #         continue
    # client_started = True
    # logging.warning('Client started')

    return True


def wait_request_or_conn(state, request, conn):
    # continue
    # ждёт пока появиться подключение
    # никаких поощрений или штрафов
    if request is None or conn is None:
        return True
    return state, 0, False, {}


def configure_tcp_socket():
    try:
        SERVER_ADDRESS = ('localhost', 9999)
        # Настраиваем сокет
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO: will configure well
        # server_socket.settimeout(10)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(SERVER_ADDRESS)
        server_socket.listen(1)
        logging.info('Simple Tcp Server is running. 2')
        return server_socket
    # TODO: exception handling
    except Exception as ex:
        raise ex


def callback_vcmi(conn, json):
    # TODO util for env step
    conn.send(json.dumps(json).encode('ascii'))
    conn.close()
