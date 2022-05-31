import threading

import os
import logging
logger = logging.getLogger(__name__)
import subprocess

def kill_vcmi():
    os.system('taskkill /IM "VCMI_server.exe" /F')
#     os.system('killall vcmiclient')
    print('Vcmi killed.')

# kill_vcmi()

def start_vcmi_test_battle(headless=False):
    vcmi_client_path_with_args = \
        r'C:\VCMI\build\bin\Release\VCMI_client.exe'
        # r'C:\VCMI\build\bin\Release\VCMI_client.exe --spectate --spectate-hero-speed 1 --spectate-battle-speed 1 --spectate-skip-battle-result --onlyAI --ai EmptyAI --disable-video --testmap C:\\VCMI\build\bin\Release\maps\template-d1.h3m'

    # print('SYSTEM')
    list_for_command = [vcmi_client_path_with_args, '--testmap', 'Maps/template_d1.h3m', '--spectate', '--spectate-hero-speed', '1', '--spectate-battle-speed', '3', '--spectate-skip-battle-result', '--onlyAI', '--ai', 'BattleML', '--disable-video']
    if headless:
        list_for_command.append('--headless')
    # print(list_for_command)
    subprocess.run(list_for_command)
    print('Vcmi started.')
    # print('start_vcmi_test_battle')


def get_thread_by_name(name):
    threads = threading.enumerate() #Threads list
    for thread in threads:
        if thread.name == name:
            return thread
