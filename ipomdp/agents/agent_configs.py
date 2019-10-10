"""
Overcooked (Stage: 1)
----------
Every stage of Overcooked will have different declarations of initial barriers and world state.
To get to respective subgoals, agent/observer has to move to grid before the subgoal.

Ingredients should be pre-determined before start of the simulation (we need to know if ingredient needs to be cooked).
In the ingredients dictionary, the ingredients can be classified under `raw` or `fresh`.
Raw ingredients need to be cooked while fresh ingredients don't need to be.
Each ingredient in the world state can hold a existing ingredient state (eg. fresh, fresh chopped)

Recipes should be pre-determined before start of the simulation (we need to know how to cook a dish).
Recipes such as pizza have required and optional ingredients which are more complicated to model so to ensure we don't over-declare key-value pairs,
we'll follow a structure when naming keys. More specifically, let's follow the required/optional, then alphabetical order.
Eg. Pizza -> Dough(Required), Tomato(Required), Cheese(Required), Mushroom(Optional), Sausage(Optional)
Eg. Pancakes -> Chocolate, Egg, Flour (All needs to be beaten, before fying all at once)

Intermediate states are assumed to be already chopped/prepared and ready to be plated. Use python sorted() to get below order.

RECIPES_PLATING_INTERMEDIATE_STATES_X = {
    'pizza': {
        'ch': ['cheese'], 
        'do': ['dough'],
        'to': ['tomato'],
        'mu': ['mushroom'],
        'sa': ['sausage'],
        'ch_do': ['cheese', 'dough'], 
        'ch_to': ['cheese', 'tomato'],
        'ch_mu': ['cheese', 'mushroom'],
        'ch_sa': ['cheese', 'sausage'],
        'do_to': ['dough', 'tomato'],
        'do_mu': ['dough', 'mushroom'],
        'do_sa': ['dough', 'sausage'],
        'to_mu': ['mushroom', 'tomato'],
        'to_sa': ['sausage', 'tomato'],
        'mu_sa': ['mushroom', 'sausage'],
        'ch_do_to': ['cheese', 'dough', 'tomato'],
        'ch_do_mu': ['cheese', 'dough', 'mushroom'],
        'ch_do_sa': ['cheese', 'dough', 'sausage'],
        'do_to_mu': ['dough', 'mushroom', 'tomato'],
        'do_to_sa': ['dough', 'sausage', 'tomato'],
        'to_mu_sa': ['mushroom', 'sausage', 'tomato'],
        'ch_do_to_mu': ['cheese', 'dough', 'mushroom', 'tomato'],
        'ch_do_to_sa': ['cheese', 'dough', 'mushroom', 'sausage'],
        'do_to_mu_sa': ['dough', 'mushroom', 'sausage', 'tomato'],
        'ch_do_to_mu_sa: ['cheese', 'dough', 'mushroom', 'sausage', 'tomato']
    }, etc.
}
"""
# BARRIERS_1 = [
#     (0,8), (1,8), (2,8), (3,8), (4,8), (5,8), (6,8), (7,8), (8,8), (9,8), (10,8), (11,8), (12,8),
#     (0,8), (0,7), (0,6), (0,5),
#     (0,4), (1,4), (2,4), (3,4), (4,4), (5,4), (6,4), (7,4), (8,4), (9,4),
#     (0,4), (0,3), (0,2), (0,1),
#     (0,0), (1, 0), (2, 0), (3,0), (4, 0), (5, 0), (6,0), (7, 0), (8, 0), (9,0), (10, 0), (11, 0),
#     (12,0), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8)
# ]

BARRIERS_1 = [
    (0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6), (0,7), (0,8), (0,9), (0,10), (0,11), (0,12),
    (1,0), (1,12),
    (2,0), (2,12),
    (3,0), (3,12),
    (4,0), (4,1), (4,2), (4,3), (4,4), (4,5), (4,6), (4,7), (4,8), (4,9), (4,12),
    (5,0), (5,12),
    (6,0), (6,12),
    (7,0), (7,12),
    (8,0), (8,1), (8,2), (8,3), (8,4), (8,5), (8,6), (8,7), (8,8), (8,9), (8,10), (8,11), (8,12)
]

VISUALIZATION_COORDS_MAPPING_1 = {
    'row_to_col': [8,7,6,5,4,3,2,1,0],
    'col_to_row': [1,2,3,4,5,6,7,8,9,10,11,12]
}

ITEMS_INITIALIZATION_1 = {
    'chopping_board': [(8,3), (8,5)],
    'extinguisher': [(1,12)],
    'plate': [(8,9), (8,10)],
    'pot': [(0,8)],
    'stove': [(0,8)],
}

INGREDIENTS_INITIALIZATION_1 = {
    # properties of ingredients
    'onion': {
        'location': [(0,3)],
        'state': 'fresh',
        'category': 'ingredient',
        'is_raw': True
    }
}

RECIPES_INGREDIENTS_COUNT_1 = {
    'onion_soup': {
        'onion': 3
    }
}

RECIPES_SERVE_TASK_1 = {
    'onion_soup': [('plate', 'cooked'), ('scoop', 'cooked'), ('serve', 'cooked')]
}

INGREDIENTS_NAMING_CONVENTION = {
    'onion': 'on'
}

RECIPES_COOKING_INTERMEDIATE_STATES_1 = {
    'on': ['onion'],
    'on_on': ['onion', 'onion'],
    'on_on_on': ['onion', 'onion', 'onion']
}

RECIPES_PLATING_INTERMEDIATE_STATES_1 = {
    'on_on_on': ['onion', 'onion', 'onion']
}

"""
WORLD_STATE
-----------
World state models where key stations are located. (Eg. chopping board - K1(3,1), K2(5,1) etc.)
World state models where agents/observers are located. (Eg. agent - A(6,8), O(6,4) etc.)
World state models where raw <ingredient>, fresh <ingredient> etc. are located.
World state models where all combinations of partially-cooked/fully-cooked dishes are located. (Eg. onion, onion-onion, onion-onion-onion)
At any one point, world state for pots are being tracked for location and burnt chance.
Dict[str: List[Optional[int, int]]]

Definitions
-----------
Following notation is in the form of dictionary key -> explanation

<To run loop to append ingredient(s) information to World state dictionary; because possibility of multiple ingredients>
collection_<ingredient> : Collection point for raw/fresh ingredient.
r_<ingredient> -> raw <ingredient>: Un-chopped ingredient that needs to be cooked. 
rc_<ingredient> -> raw chopped <ingredient>: Chopped ingredient that needs to be cooked.
co_<ingredient> -> cooked <ingredient>: Ingredient that is cooked.
f_<ingredient> -> fresh <ingredient>: Ingredient that does not need to be cooked.
fc_<ingredient> -> fresh chopped <ingredient>: Chopped ingredient that does not need to be cooked.

d_plates -> dirty plates: Plates that require washing before use.
c_plates -> clean plates: Plates that do not require washing before use.
pp_plates -> partially plated plates: Plates that hold ingredients (in-preparation). 
fp_plates -> fully plated plates: Plates that hold ingredients (ready to-be-served).
e_boards -> empty chopping board: Chopping boards that are empty.
f_boards -> filled chopping board: Chopping boards that are filled.
e_stoves -> empty stoves: Stoves that are empty.
f_stoves -> filled stoves: Stoves that are filled.
e_pots -> empty pots: Pots that are empty.
pc1_pots -> partially cooked 1 <ingredient> pots: Pots with 1 cooking onion. (with timer countdown)
pc2_pots -> partially cooked 2 <ingredient> pots: Pots with 2 cooking onions. (with timer countdown)
pc3_pots -> partially cooked 3 <ingredient> pots: Pots with 3 cooking onions. (with timer countdown)
pco1_pots -> cooked 1 <ingredient> pot: Pot with 1 cooked onion.
pco2_pots -> cooked 2 <ingredient> pot: Pot with 2 cooked onions.
pco3_pots -> cooked 3 <ingredient> pot: Pot with 3 cooked onions.
on_pots -> pots on stove: Pots that are on the stove.
off_pots -> pots off stove: Pots that are off the stove.
burning_pots -> burning pots: Pots that are on the verge of burning.
burnt_pots -> burnt pots: Pots that are burnt.
sc_<X> -> Service counters to serve food.
r_plates -> Plates retuning venue after <X> seconds of food consumption.
basin: Basin to wash dirty plates.

agent: Location of agent
observer: Location of observer
(is it done?)

To clear chopping board space, find nearest empty tabletop grid and shift it there
"""
WORLD_STATE_1 = {
    'valid_optimal_table_tops': [
        (1,4), (2,4), (3,4), (4,4), (5,4), (6,4), (7,4), (8,4), (9,4)
    ],
    'invalid_optimal_table_tops': [],
    'valid_cells': [
        (1,1), (1,2), (1,3), (1,5), (1,6), (1,7),
        (2,1), (2,2), (2,3), (2,5), (2,6), (2,7),
        (3,1), (3,2), (3,3), (3,5), (3,6), (3,7),
        (4,1), (4,2), (4,3), (4,5), (4,6), (4,7),
        (5,1), (5,2), (5,3), (5,5), (5,6), (5,7),
        (6,1), (6,2), (6,3), (6,5), (6,6), (6,7),
        (7,1), (7,2), (7,3), (7,5), (7,6), (7,7),
        (8,1), (8,2), (8,3), (8,5), (8,6), (8,7),
        (9,1), (9,2), (9,3), (9,5), (9,6), (9,7),
        (10,1), (10,2), (10,3), (10,4), (10,5), (10,6), (10,7),
        (11,1), (11,2), (11,3), (11,4), (11,5), (11,6), (11,7)
    ],
    'new_valid_cells': [
        (1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (1,8), (1,9), (1,10), (1,11),
        (2,1), (2,2), (2,3), (2,4), (2,5), (2,6), (2,7), (2,8), (2,9), (2,10), (2,11),
        (3,1), (3,2), (3,3), (3,4), (3,5), (3,6), (3,7), (3,8), (3,9), (3,10), (3,11),
        (4,10), (4,11),
        (5,1), (5,2), (5,3), (5,4), (5,5), (5,6), (5,7), (5,8), (5,9), (5,10), (5,11),
        (6,1), (6,2), (6,3), (6,4), (6,5), (6,6), (6,7), (6,8), (6,9), (6,10), (6,11),
        (7,1), (7,2), (7,3), (7,4), (7,5), (7,6), (7,7), (7,8), (7,9), (7,10), (7,11),
    ],
    'ingredient_onion': [(0,3)],
    'service_counter': [(6,0), (7,0)],
    'agent': [(8,6)],
    'observer': [(6,6)],
    'board_1': [(3,0)],
    'board_2': [(5,0)],
    'r_onion': [(3,8)],
    'stove_1': [(8,8)],
    'plate_1': [(9,0)],
    'plate_2': [(10,0)],
    'basin': [(12,5)],
    'bin': [(12,1)],
    'sc_1': [(0,1)],
    'sc_2': [(0,2)],
    'pot_1': [(8,8)],
    'd_plates': [],
    'c_plates': [(9,0), (10,0)],
    'pp_plates': [],
    'fp_plates': [],
    'e_boards': [(3,0), (5,0)],
    'f_boards': [],
    'e_stoves': [],
    'f_stoves': [(8,8)],
    'e_pots': [(8,8)],
    'pc1_pots': [],
    'pc2_pots': [],
    'pc3_pots': [],
    'pco1_pots': [],
    'pco2_pots': [],
    'pco3_pots': [],
    'on_pots': [(8,8)],
    'off_pots': [],
    'burning_pots': [],
    'burnt_pots': []
}

"""
Actions
-------
TO-DO: Actions that can be performed.
"""
ACTIONS = {
    0: 'MOVE_LEFT',
    1: 'MOVE_RIGHT',
    2: 'MOVE_UP',
    3: 'MOVE_DOWN',
    4: 'MOVE_DIAGONAL_LEFT_UP',
    5: 'MOVE_DIAGONAL_RIGHT_UP',
    6: 'MOVE_DIAGONAL_LEFT_DOWN',
    7: 'MOVE_DIAGONAL_RIGHT_DOWN',
    8: 'STAY',
    9: 'PICK',
    10: 'CHOP',
    11: 'COOK',
    12: 'SCOOP',
    13: 'SERVE'
}


"""
Rewards
-------
TO-DO: Rewards that have floating values.
"""
REWARDS_1 = {
    'MOVE_LEFT': -1,
    'MOVE_RIGHT': -1,
    'MOVE_UP': -1,
    'MOVE_DOWN': -1,
    'MOVE_DIAGONAL_LEFT_UP': -2,
    'MOVE_DIAGONAL_RIGHT_UP': -2,
    'MOVE_DIAGONAL_LEFT_DOWN': -2,
    'MOVE_DIAGONAL_RIGHT_DOWN': -2,
    'STAY': -2,
    'PICK': 10, # consider changing to 'create'
    'CHOP': 30,
    'COOK': 45,
    'SCOOP': 30,
    'SERVE': 100
}

"""
TO-DO: More world states
"""


# Current World State
VISUALIZATION_COORDS_MAPPING = VISUALIZATION_COORDS_MAPPING_1
WORLD_STATE = WORLD_STATE_1
BARRIERS = BARRIERS_1
ITEMS_INITIALIZATION = ITEMS_INITIALIZATION_1
INGREDIENTS_INITIALIZATION = INGREDIENTS_INITIALIZATION_1
RECIPES_INGREDIENTS_COUNT = RECIPES_INGREDIENTS_COUNT_1
RECIPES_SERVE_TASK = RECIPES_SERVE_TASK_1
RECIPES_COOKING_INTERMEDIATE_STATES = RECIPES_COOKING_INTERMEDIATE_STATES_1
RECIPES_PLATING_INTERMEDIATE_STATES = RECIPES_PLATING_INTERMEDIATE_STATES_1
REWARDS = REWARDS_1