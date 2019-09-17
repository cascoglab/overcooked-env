from typing import Dict
from typing import List
from typing import Tuple

# import ray
from collections import defaultdict
import matplotlib.pyplot as plt

from agent_configs import *
from astart_search import AStarGraph
from overcooked import *


class BaseAgent:
    def __init__(
        self,
        agent_id,
        location
    ) -> None:
        """
        Parameters
        ----------
        agent_id: str
            a unique id allowing the map to identify the agents
        location: Tuple[int,int]
            x-y coordinate of agent
        """

        self.agent_id = agent_id
        self.location = location

    @property
    def action_space(self):
        """
        Identify the dimension and bounds of the action space.

        MUST BE implemented in new environments.
        """
        raise NotImplementedError

    def action_map(self, action_number):
        """Maps action_number to a desired action in the map"""
        raise NotImplementedError

class OvercookedAgent(BaseAgent):
    def __init__(
        self,
        agent_id,
        location,
        barriers,
        ingredients,
        cooking_intermediate_states,
        plating_intermediate_states,
        goals=None,
    ) -> None:
        super().__init__(agent_id, location)
        self.goals = goals
        self.cooking_intermediate_states = cooking_intermediate_states
        self.plating_intermediate_states = plating_intermediate_states
        self.get_astar_map(barriers)
        self.initialize_world_state(ITEMS_INITIALIZATION)
        self.update_world_state_with_ingredients(ingredients)

    def get_astar_map(self, barriers: List[List[Tuple[int,int]]]) -> None:
        self.astar_map = AStarGraph(barriers)

    def update_world_state_with_ingredients(self, ingredients: Dict[str, List[str]]):
        for ingredient in ingredients:
            self.world_state['ingredient_'+ingredient] = []
    
    def update_world_state_with_pots(self, pot_coords: List[Tuple[int,int]]):
        for pot_num in range(len(pot_coords)):
            self.world_state['pot_'+str(pot_num)] = Pot('utensil', pot_coords[pot_num])
    
    # TO-DO: Shift to World Env
    def initialize_world_state(self, items: Dict[str, List[Tuple]]):
        """ 
        world_state:
            a dictionary indicating world state (coordinates of items in map)
        """
        self.world_state = defaultdict(list)
        self.world_state['valid_cells'] = WORLD_STATE['valid_cells']
        self.world_state['agent'] = WORLD_STATE['agent'] # to be removed

        for item in items:
            if item == 'chopping_boards':
                for i_state in items[item]:
                    new_item = ChoppingBoard('utensils', i_state)
                    self.world_state[item].append(new_item)
            elif item == 'extinguisher':
                for i_state in items[item]:
                    new_item = Extinguisher('safety', i_state)
                    self.world_state[item].append(new_item)
            elif item == 'plate':
                for i_state in items[item]:
                    new_item = Plate('utensils', i_state)
                    self.world_state[item].append(new_item)
            elif item == 'pot':
                for i_state in items[item]:
                    new_item = Pot('utensils', i_state)
                    self.world_state[item].append(new_item)
            elif item == 'stove':
                for i_state in items[item]:
                    new_item = Stove('utensils', i_state)
                    self.world_state[item].append(new_item)

    def calc_travel_cost(self, items: List[str], items_coords: List[List[Tuple[int,int]]]):
        # get valid cells for each goal
        item_valid_cell_states = defaultdict(list)
        for item_idx in range(len(items)):
            item_valid_cell_states[items[item_idx]] = self.find_valid_cell(items_coords[item_idx])

        travel_costs = defaultdict(tuple)
        for item_idx in range(len(items)):
            cur_item_instances = items_coords[item_idx]
            for cur_item_instance in cur_item_instances:
                try:
                    valid_cells = item_valid_cell_states[items[item_idx]][cur_item_instance]
                    for valid_cell in valid_cells:
                        temp_item_instance = self.AStarSearch(valid_cell)
                        if not travel_costs[items[item_idx]]:
                            travel_costs[items[item_idx]] = (temp_item_instance[0], temp_item_instance[1], cur_item_instance)
                        else:
                            # Only replace if existing travel cost is greater (ensure only 1 path is returned given same cost)
                            if travel_costs[items[item_idx]][1] > temp_item_instance[1]:
                                travel_costs[items[item_idx]] = (temp_item_instance[0], temp_item_instance[1], cur_item_instance)
                            continue
                except KeyError:
                    raise KeyError('No valid path to get to item!')

        return travel_costs

    def AStarSearch(self, dest_coords: Tuple[int,int]):
        """
        A* Path-finding algorithm
        Type: Heuristic-Search - Informed Search Algorithm

        F: Estimated movement cost of start to end going via this position
        G: Actual movement cost to each position from the start position
        H: heuristic - estimated distance from the current node to the end node

        It is important for heuristic to always be an underestimation of the total path, as an overestimation
        will lead to A* searching through nodes that may not be the 'best' in terms of f value.
        """
 
        start = self.world_state['agent'][0]
        end = dest_coords
        G = {}
        F = {}
    
        # Initialize starting values
        G[start] = 0 
        F[start] = self.astar_map.heuristic(start, end)
    
        closedVertices = set()
        openVertices = set([start])
        cameFrom = {}
    
        while len(openVertices) > 0:
            # Get the vertex in the open list with the lowest F score
            current = None
            currentFscore = None
            for pos in openVertices:
                if current is None or F[pos] < currentFscore:
                    currentFscore = F[pos]
                    current = pos
    
            # Check if we have reached the goal
            if current == end:
                # Retrace our route backward
                path = [current]
                while current in cameFrom:
                    current = cameFrom[current]
                    path.append(current)
                path.reverse()
                return path, F[end] # Done!
    
            # Mark the current vertex as closed
            openVertices.remove(current)
            closedVertices.add(current)
    
            # Update scores for vertices near the current position
            for neighbour in self.astar_map.get_vertex_neighbours(current):
                if neighbour in closedVertices: 
                    continue # We have already processed this node exhaustively
                candidateG = G[current] + self.astar_map.move_cost(current, neighbour)
    
                if neighbour not in openVertices:
                    openVertices.add(neighbour) # Discovered a new vertex
                elif candidateG >= G[neighbour]:
                    continue # This G score is worse than previously found
    
                #Adopt this G score
                cameFrom[neighbour] = current
                G[neighbour] = candidateG
                H = self.astar_map.heuristic(neighbour, end)
                F[neighbour] = G[neighbour] + H
    
        raise RuntimeError("A* failed to find a solution")

    # def generate_goals_as_dags(self, goal):
    #     """
    #     Given new goals, convert goals to subgoals in DAG structure.
    #     """
    #     goal_required_ws = 
    #     dag = Graph(directed=True)
    #     print(dag)


    def find_best_goal(self):
        """
        Finds action which maximizes utility given world state from possible action space
        Returns
        -------
        action: Action that maximizes utility given world state -> str

        TO-DO: Call `calc_travel_cost` multiple times for possible subgoals
        """
        return

    def cook_ingredients(self):
        """
        Cooks dish and keeps track of timer.
        """
        # Timer(10, cook, [args]).start()
        return

    def find_valid_cell(self, item_coords: List[Tuple[int,int]]) -> Tuple[int,int]:
        """
        Items can only be accessible from Up-Down-Left-Right of item cell.
        Get all cells agent can step on to access item.

        Returns
        -------
        all_valid_cells: Dict[str,List[Tuple[int,int]]]
        """
        all_valid_cells = defaultdict(list)
        # item_instance is Tuple[int,int]
        for item_instance in item_coords:
            if (item_instance[0], item_instance[1]+1) in self.world_state['valid_cells']:
                all_valid_cells[item_instance].append((item_instance[0], item_instance[1]+1))
            elif (item_instance[0], item_instance[1]-1) in self.world_state['valid_cells']:
                all_valid_cells[item_instance].append((item_instance[0], item_instance[1]-1))
            elif (item_instance[0]-1, item_instance[1]) in self.world_state['valid_cells']:
                all_valid_cells[item_instance].append((item_instance[0]-1, item_instance[1]))
            elif (item_instance[0]+1, item_instance[1]) in self.world_state['valid_cells']:
                all_valid_cells[item_instance].append((item_instance[0]+1, item_instance[1]))

        return all_valid_cells

    def pick(self, path: List[Tuple[int,int]], item: Item) -> None:
        """
        This action assumes agent has already done A* search and decided which goal state to achieve.
        Prerequisite
        ------------
        - Item object passed to argument should be item instance
        - At grid with accessibility to item [GO-TO]
        
        Returns
        -------
        Pick up item
        - Check what item is picked up [to determine if we need to update world state of item]

        TO-CONSIDER: 
        Do we need to check if agent is currently holding something?
        Do we need to set item coord to agent coord when the item is picked up?
        """
        self.move(path)
        if type(item) == Ingredient:
            if item.is_new:
                item.is_new = False
                self.world_state['ingredient_'+item.name].append(item) if item.is_raw else self.world_state['ingredient_'+item.name].append(item)
            self.holding = item


    def drop(self, path: List[Tuple[int,int]], item: Item, drop_coord: Tuple[int,int]) -> None:
        """
        This action assumes agent is currently holding an item.
        Prerequisite
        ------------
        - At grid with accessibility to dropping coord.
        Drop item <X>.
        """
        self.move(path)
        if type(item) == Ingredient:
            self.world_state['ingredient_'+item.name][item.id]['location'] = drop_coord
            self.holding = None

    def move(self, path: List[Tuple[int,int]]) -> None:
        """
        - Finds item in world state.
        - Go to grid with accessibility to item.

        Parameters
        ----------
        path: for animation on grid to happen
        """
        for step in path:
            # Do animation (sleep 0.5s?)
            self.world_state[self.agent_id] = step
        self.location = path[-1]


def main():
    # ray.init(num_cpus=4, include_webui=False, ignore_reinit_error=True)
    
    oc_agent = OvercookedAgent(
        'Agent',
        (8,6),
        BARRIERS,
        INGREDIENTS,
        RECIPES_COOKING_INTERMEDIATE_STATES,
        RECIPES_PLATING_INTERMEDIATE_STATES)

    results = oc_agent.calc_travel_cost(['c_plates', 'e_boards'], [WORLD_STATE['c_plates'], WORLD_STATE['e_boards']])
    print(results)
    for subgoal in results:
        print("Goal -> ", subgoal)
        print("Route -> ", results[subgoal][0])
        print("Cost -> ", results[subgoal][1])

        plt.plot([v[0] for v in results[subgoal][0]], [v[1] for v in results[subgoal][0]])
        for barrier in [BARRIERS_1]:
            plt.plot([v[0] for v in barrier], [v[1] for v in barrier])
        plt.xlim(-1,13)
        plt.ylim(-1,9)
        plt.show()


if __name__ == '__main__':
    main()
