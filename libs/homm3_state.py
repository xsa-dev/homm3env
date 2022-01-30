from typing import Dict

from datetime import datetime
import logging
logger = logging.getLogger(__name__)

BLOCK_LOGIC = True
DEFAULT_LOGIC = False
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
        self.last_team = None

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

    def get_winner(self):
        if self.last_team == USER:
            self.winner = USER
        else:
            self.winner = COMPUTER

    def json_handler_logic(self, request) -> Dict:
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
