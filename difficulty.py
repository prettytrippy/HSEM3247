import numpy as np

MAX_LEVEL = 100

def get_num_holds(difficulty):
    # Number of holds scales logarithmically, but probably needs to grow faster
    return int(np.log(difficulty * 4)) + 1

def get_speed(difficulty):
    # Speed scales w square root
    return int(np.sqrt(difficulty * 8)) + 1

def get_erosion_chance(difficulty):
    # Erosion chance is constant, for now
    return 0.05

def get_death_chance(difficulty):
    # Death chance exponentially approaches 1 as we reach level MAX_LEVEL
    return np.exp(difficulty-MAX_LEVEL)

def get_params_from_difficulty(difficulty):
    return get_num_holds(difficulty), get_speed(difficulty), get_erosion_chance(difficulty), get_death_chance(difficulty)