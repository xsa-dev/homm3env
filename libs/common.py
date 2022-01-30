import threading

import os
import logging
logger = logging.getLogger(__name__)


def kill_vcmi():
    os.system('killall vcmiclient')
    logging.info('Vcmi killed.')

kill_vcmi()

def start_vcmi_test_battle(headless=False):
    vcmi_client_path_with_args = \
        '/Users/xsa-osx/DEV/cmake/bin/vcmiclient --spectate --spectate-hero-speed 1 \
          --spectate-battle-speed 1 --spectate-skip-battle-result --onlyAI --ai EmptyAI \
           --disable-video --testmap Maps/template-d1.h3m'
    if headless:
        vcmi_client_path_with_args += ' --headless'
    os.system(vcmi_client_path_with_args + ' > /dev/null 2>&1')
    logging.info('Vcmi started.')


def get_thread_by_name(name):
    threads = threading.enumerate() #Threads list
    for thread in threads:
        if thread.name == name:
            return thread
