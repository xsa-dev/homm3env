from time import time
from homm3_b import HoMM3_B
from datetime import datetime
import argparse
import logging
import random
import sys

import time

#### TEST ITERATIONS ####
EPISODES = 2
#########################


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/{str(datetime.now().date())}.log"),
    ]
)


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
            logging.debug('START SLEEP')
            time.sleep(3)
            logging.debug('STOP SLEEP')

            # ждем создания клиент
            # if not check_client_started():
            #    continue            # ждем включения  tcp сервиса
            # if check_connection(env, conn, server_last_packet_time, CONNECTION_TIMEOUT):
            #    continue

            # if conn is None:
            #     if env.server_last_packet_time is not None:
            #         if datetime.now().timestamp() - env.server_last_packet_time > 20.0:
            #             env.hard_reset()
            #             # server_last_packet_time = datetime.now().timestamp()
            #             # logging.warning('Service not respond.')
            #             # kill_vcmi()
            #             # env.start_vcmi_threaded()
            #     continue



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
