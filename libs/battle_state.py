import random
from cmath import log
import json
from typing import Dict
from datetime import datetime
import logging
import deprecation

logger = logging.getLogger(__name__)

# TODO: now here, later in config.yaml from main.py
BYTES_LENGHT = 32000
BLOCK_LOGIC = True
FAKE_TARGET = False
DEFAULT_LOGIC = False
COMPUTER = 'COMPUTER'
USER = 'ML'
TIMEOUT = 0.1
IS_SINGLED_USER = True
WRITE_REQUEST = False
LOG_INFO = False


###########################


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class MlService:
    def reset(self):
        # todo: DRY
        self.current_team = USER
        self.tcp_responses_counter = 0
        self.last_connection_timestamp = 0
        self.is_service_active = None
        self.current_connection = None

        # game state variables
        self.game_end = False
        self.winner = None
        self.last_team = None

        # possible attacks
        self.possible_attacks = None

        # possible movies
        self.possible_moves = None

        # computer state
        self.is_computer = None
        self.computer_units = None

        # human state
        self.is_player = None
        self.player_units = None

        # army's properties
        self.left_total_health = None
        self.left_army_count = [-1, -1]
        self.left_max_damage = None
        self.left_min_damage = None
        self.left_attack = None

        self.right_total_health = None
        self.right_army_count = [-1, -1]
        self.right_max_damage = None
        self.right_min_damage = None
        self.right_attack = None

        # TODO: compute variables for get battle result function
        self.last_computer_request = None
        self.last_ml_request = None
        self.request = None

    def __init__(self):
        # server state variables (default)
        self.current_team = None
        self.tcp_responses_counter = 0
        self.last_connection_timestamp = 0
        self.is_service_active = None
        self.current_connection = None

        # game state variables
        self.game_end = False
        self.winner = None
        self.last_team = None

        # possible attacks
        self.possible_attacks = None

        # possible movies
        self.possible_moves = None

        # computer state
        self.is_computer = None
        self.computer_units = None

        # human state
        self.is_player = None
        self.player_units = None

        # army's properties
        self.left_total_health = None
        self.left_army_count = [-1, -1]
        self.left_max_damage = None
        self.left_min_damage = None
        self.left_attack = None

        self.right_total_health = None
        self.right_army_count = [-1, -1]
        self.right_max_damage = None
        self.right_min_damage = None
        self.right_attack = None

        # TODO: compute variables for get battle result function
        self.last_computer_request = None
        self.last_ml_request = None
        self.request = None

    def get_service_active_state(self) -> bool:
        # show timeout service state response
        current_timestamp = datetime.now().timestamp()
        if (TIMEOUT + self.last_connection_timestamp) - current_timestamp >= 0:
            return True
        else:
            logging.error('Timeout!! Too slow...')
            return False

    def get_winner(self):
        # TODO: fix logic after research
        if self.right_army_count is not None:
            if self.right_army_count[1] > 10:
                return False

            # TODO: logic fix fix fix
            if self.left_army_count[1] > 25 and self.right_army_count[1] < 5:
                # todo: fix logic for army health and attack properties calculating
                if self.right_army_count[1] > self.left_army_count[1]:
                    self.winner = COMPUTER
                    self.game_end = True
                    return True

                if self.left_army_count[1] > self.right_army_count[1]:
                    self.winner = USER
                    self.game_end = True
                    return True
            else:
                return False

    def get_possible_attacks(self):
        return len(self.request['actions']['possibleAttacks'])

    def get_possible_moves(self):
        return len(self.request['actions']['possibleMoves'])

    def get_total_health(self, side=None):
        total_health = 0
        for stack in self.request['stacks']:
            if stack['stackCount'] is not None:
                if self.current_team == COMPUTER:
                    if stack['side'] == 1:
                        # print(stack['id'])
                        total_health += int(stack['healthLeft'])
                if self.current_team == USER:
                    if stack['side'] == 0:
                        # print(stack['id'])
                        total_health += int(stack['healthLeft'])
        return total_health

    def get_army_count(self, side=None):
        if side is None:
            raise Exception('Specify side!')

        army_count_computer = 0
        army_count_user = 0
        for stack in self.request['stacks']:
            if stack['stackCount'] is not None:
                if stack['side'] == 1:
                    army_count_computer += int(stack['stackCount'])
                if stack['side'] == 0:
                    army_count_user += int(stack['stackCount'])

        # len of states must be size 2. 0 - for last and 1 - for current
        if side == COMPUTER:
            if len(self.right_army_count) == 2:
                self.right_army_count.pop(0)
                self.right_army_count.append(army_count_computer)
            else:
                raise Exception('Desync computer army counter!')

        if side == USER:
            if len(self.left_army_count) == 2:
                self.left_army_count.pop(0)
                self.left_army_count.append(army_count_user)
            else:
                raise Exception('Desync user army counter!')

        return army_count_computer if side == COMPUTER else army_count_user

    def get_army_attack_max_damage(self, side=None):
        army_max_damage = 0
        for stack in self.request['stacks']:
            if stack['stackCount'] is not None:
                if self.current_team == COMPUTER:
                    if stack['side'] == 1:
                        army_max_damage += int(stack['maxDamage'])
                if self.current_team == USER:
                    if stack['side'] == 0:
                        army_max_damage += int(stack['maxDamage'])
        return army_max_damage

    def get_army_attack_min_damage(self, side=None):
        army_min_damage = 0
        for stack in self.request['stacks']:
            if stack['stackCount'] is not None:
                if self.current_team == COMPUTER:
                    if stack['side'] == 1:
                        army_min_damage += int(stack['minDamage'])
                if self.current_team == USER:
                    if stack['side'] == 0:
                        army_min_damage += int(stack['minDamage'])
        return army_min_damage

    def get_army_attack(self, side=None):
        army_attack = 0
        for stack in self.request['stacks']:
            if stack['stackCount'] is not None:
                if self.current_team == COMPUTER:
                    if stack['side'] == 1:
                        army_attack += int(stack['attack'])
                if self.current_team == USER:
                    if stack['side'] == 0:
                        army_attack += int(stack['attack'])
        return army_attack

    def update(self, request):
        self.tcp_responses_counter += 1
        self.last_connection_timestamp = datetime.now().timestamp()
        self.is_service_active = self.get_service_active_state()
        self.request = request

        if request['currentSide'] == 0:
            self.current_team = USER
            self.is_computer = False
            self.is_player = True
            self.last_ml_request = request
            self.possible_attacks = self.get_possible_attacks()
            self.possible_moves = self.get_possible_moves()

        self.get_army_count(side=USER)
        self.left_total_health = self.get_total_health(side=USER)
        self.left_attack = self.get_army_attack(side=USER)
        self.left_max_damage = self.get_army_attack_max_damage(side=USER)
        self.left_min_damage = self.get_army_attack_min_damage(side=USER)

        if request['currentSide'] == 1:
            self.current_team = COMPUTER
            self.is_computer = True
            self.is_player = False
            self.last_computer_request = request
            self.possible_attacks = self.get_possible_attacks()
            self.possible_moves = self.get_possible_moves()

        self.get_army_count(side=COMPUTER)
        self.right_total_health = self.get_total_health(side=COMPUTER)
        self.right_attack = self.get_army_attack(side=COMPUTER)
        self.right_max_damage = self.get_army_attack_max_damage(side=COMPUTER)
        self.right_min_damage = self.get_army_attack_min_damage(side=COMPUTER)

        if LOG_INFO:
            logging.info(f'>> {self.current_team} #{self.tcp_responses_counter} at {self.last_connection_timestamp} >>')
            logging.info(f'State:')
            logging.info(f'possible attacks: {self.possible_attacks}')
            logging.info(f'possible moves: {self.possible_moves}')

            # @@@@
            logging.info(f'Scores:')
            logging.info(f'army count (computer): {str(self.right_army_count)}')
            logging.info(f'army total health (computer): {str(self.right_total_health)}')
            logging.info(f'army damage (computer): mxd: {str(self.right_max_damage)}, mid {str(self.right_min_damage)}')
            logging.info(f'army attack (computer): atc: {str(self.right_attack)}')
            logging.info('@@@ VS @@@')
            logging.info(f'army count (ml): {self.left_army_count}')
            logging.info(f'army total health (ml): {self.left_total_health}')
            logging.info(f'army damage (ml): mxd: {str(self.left_max_damage)}, mid {str(self.left_min_damage)}')
            logging.info(f'army attack (ml): atc: {str(self.left_attack)}')

        if self.get_winner():
            logging.log(logging.WARNING, f'WINNER IS: {str(self.winner)}')

        if WRITE_REQUEST:
            logging.info(f'request: {request}')

    def make_prediction(self, request, action: int, target_varible=0):
        # TODO: remove fake logic!!
        # TODO: this is fake logic, need implement real ml magic
        if random.randint(1, 10) == 1:
            # TODO: how to wait?
            pass
        if random.randint(1, 10) == 2:
            # TODO: how defend?
            pass

        if len(request["actions"]["possibleAttacks"]) > 0 and FAKE_TARGET:
            attack = request["actions"]["possibleAttacks"][0]
            action = {
                "type": 1 if attack["shooting"] else 2,
                "targetId": attack["defenderId"],
                "moveToHex": attack["moveToHex"]
            }
        elif len(request["actions"]["possibleAttacks"]) > 0:
            # random target
            count = len(request["actions"]["possibleAttacks"]) - 1 if (len(
                request["actions"]["possibleAttacks"]) - 1) > 0 else 0
            action = random.randint(0, count)
            attack = request["actions"]["possibleAttacks"][action]
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

    def dump_to_json(self, research_folder):
        #  TODO: implement save responses from RAM for complete research
        # TODO: note: need only if problems with engine and reboot not works well
        pass

    def send_heartbeat_to_vcmi_service(self):
        # TODO: implement logic for heartbeat current vcmi instance
        pass
