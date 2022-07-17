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
        self.left_army_count = None
        self.left_max_damage = None
        self.left_min_damage = None
        self.left_attack = None

        self.right_total_health = None
        self.right_army_count = None
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
        self.left_army_count = None
        self.left_max_damage = None
        self.left_min_damage = None
        self.left_attack = None

        self.right_total_health = None
        self.right_army_count = None
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
            if self.possible_attacks == 1:
                # todo: fix logic for army health and attack properties calculating
                if self.current_team == USER:
                    self.winner = USER
                    self.game_end = True
                    return True

            if self.possible_attacks == 1:
                # todo: fix logic for army health and attack properties calculating
                if self.current_team == COMPUTER:
                    self.winner = COMPUTER
                    self.game_end = True
                    return True

        if self.last_team == USER:
            self.winner = USER
        else:
            self.winner = COMPUTER

    def get_possible_attacks(self):
        return len(self.request['actions']['possibleAttacks'])

    def get_possible_moves(self):
        return len(self.request['actions']['possibleMoves'])

    def get_total_health(self):
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

    def get_army_count(self):
        army_count = 0
        for stack in self.request['stacks']:
            if stack['stackCount'] is not None:
                if self.current_team == COMPUTER:
                    if stack['side'] == 1:
                        army_count += int(stack['stackCount'])
                if self.current_team == USER:
                    if stack['side'] == 0:
                        army_count += int(stack['stackCount'])
        return army_count

    def get_army_attack_max_damage(self):
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

    def get_army_attack_min_damage(self):
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

    def get_army_attack(self):
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
            self.left_army_count = self.get_army_count()
            self.left_total_health = self.get_total_health()
            self.left_attack = self.get_army_attack()
            self.left_max_damage = self.get_army_attack_max_damage()
            self.left_min_damage = self.get_army_attack_min_damage()

        if request['currentSide'] == 1:
            self.current_team = COMPUTER
            self.is_computer = True
            self.is_player = False
            self.last_computer_request = request
            self.possible_attacks = self.get_possible_attacks()
            self.possible_moves = self.get_possible_moves()
            self.right_army_count = self.get_army_count()
            self.right_total_health = self.get_total_health()
            self.right_attack = self.get_army_attack()
            self.right_max_damage = self.get_army_attack_max_damage()
            self.right_min_damage = self.get_army_attack_min_damage()

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

    def prediction(self, request, target_varible=0):
        # TODO: this is fake logic, need implement real ml magic
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
        # logging.info(f'@@@@ {self.last_connection_timestamp} @@@@')
        return action

    def dump_to_json(self, research_folder):
        #  TODO: implement save responses from RAM for complete research
        # TODO: note: need only if problems with engine and reboot not works well
        pass

    def send_heartbeat_to_vcmi_service(self):
        # TODO: implement logic for heartbeat current vcmi instance
        pass
