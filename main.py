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
#### TEST VARIABLES ####
IS_HEADLESS = False


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
    env = HoMM3_B(
        headless=IS_HEADLESS
        )

    for episode in range(1, EPISODES + 1):
        # reset сервер и vcmi
        state = env.reset()
        done = False
        score = 0
        # пока игра не закончена
        while not done:
            # выполняем
            env.render()
            # выполнем выбор действия
            action = random.choice(env.actions())
            # получаем состояние, награду, признак завершения, информацию
            try:
                n_state, reward, done, info = env.step(action)
            except Exception as ex:
                logging.error(str(ex))
                n_state, reward, done, info = env.state, 0, False, {
                    'error': str(ex)}
                env.reset()
            # увеличиванием награду
            score += reward
            logging.info('$$$ EPISODE: {}: Step: {} Score: {} Reward: {} Action: {} Done: {} Info: {}'.format(
                episode,
                n_state, score, reward, action, done, info))

    logging.info('### Episodes:{}, Score:{} ###'.format(episode, score))
    env.kill()
