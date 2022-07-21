import time

from homm3battle import HoMM3Battle
from datetime import datetime
import argparse
import logging
import random
import sys

#### TEST ITERATIONS ####
EPISODES = 10
#### TEST VARIABLES ####
IS_HEADLESS = False

## DEF ###
done = False

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/{str(datetime.now().date())}.log"),
    ]
)


def parse_options():
    # TODO: here options for ENV
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', dest='port', default=9998,
                        help='tcp server port', type=int)
    parser.add_argument('--host', dest='host', default='localhost',
                        help='tcp host url')
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    options = parse_options()

    # ENV test
    env = HoMM3Battle(
        headless=IS_HEADLESS
    )

    # TODO: preprocess logic to ML models for baselines
    for episode in range(1, EPISODES + 1):
        # reset сервер и vcmi
        state = env.reset()

        # init value of env variables
        done, score = False, 0
        while not done:
            env.render()
            # выполняем выбор действия
            action = random.choice(env.actions())
            steps, reward, done, info = env.step(action)
            score += reward
            logging.info('$$$ EPISODE: {}: Step: {} Score: {} Reward: {} Action: {} Done: {} Info: {}'.format(
                episode, steps, score, reward, action, done, info))

    logging.info('### Episodes:{}, Score:{} ###'.format(episode, score))
    env.kill()
