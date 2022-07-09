import json

def get_winner():
  # winner is totalHealth grather then 
  # winner is player with max totalHealth on last round
  # difference between different players is key of success
  pass


if __name__ == '__main__':
  ml = open('/home/xsa-lin/DEV/homm3env/research/ml_last_battle.json')
  computer = open('/home/xsa-lin/DEV/homm3env/research/computer_last_battle.json')
  ml_data = json.load(ml)
  computer_date = json.load(computer)
  print('')