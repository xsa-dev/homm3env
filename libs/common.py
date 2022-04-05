import threading

import os
import logging
logger = logging.getLogger(__name__)


def kill_vcmi():
    os.system("killall -9 vcmiserver")
    os.system("killall -9 vcmiclient")
    logging.info('vcmi killed.')

# kill_vcmi()

def start_vcmi_test_battle(headless=False, release=True):
    # build paths
    if release:
        bin_path = '/Users/xsa-osx/DEV/build-vcmi-Qt_6_1_2_for_macOS-Release/bin/vcmiclient'
    if not release:
        bin_path = '/Users/xsa-osx/DEV/cmake/bin/vcmiclient'

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
    logging.info('Vcmi started.')


def get_thread_by_name(name):
    threads = threading.enumerate() #Threads list
    for thread in threads:
        if thread.name == name:
            return thread
