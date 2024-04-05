from dataclasses import dataclass
from typing import Any

import graph

from pgtg.constants import OBSTACLE_MASK_NAMES, OBSTACLE_NAMES


@dataclass
class MapPlan:
    """Dataclass representing a map that has been generated but can't be used for running an episode yet."""

    width: int
    height: int
    tiles: list[list[dict[str, Any]]]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MapPlan":
        """Creates a MapPlan object from a dictionary."""

        return cls(
            width=data["width"],
            height=data["height"],
            tiles=data["map"],
        )


def generate_map(
    width: int,
    height: int,
    percentage_of_connections: float,
    rng,
    *,
    obstacle_probability: float = 0,
    ice_probability_weight: float = 1,
    broken_road_probability_weight: float = 1,
    sand_probability_weight: float = 1,
) -> MapPlan:
    """Generates a map object based on the provided parameters.

    Args:
        width: The width of the generated map object in tiles.
        height: The height of the generated map object in tiles.
        percentage_of_connections: The percentage of connections that are generated compared to all possible connection that could exist. A value of 1 lead each tile being connected to all neighbors. The start and end of the map are always connected, even if a value of 0 is chosen.
        rng: (np rng) A rng that is used for all randomness.
        obstacle_probability: Default 0. The probability of a tile having a obstacle.
        ice_probability_weight: Default 1. Relative weight of the ice obstacle when choosing a random obstacle.
        broken_road_probability_weight: Default 1. Relative weight of the broken road obstacle when choosing a random obstacle.
        sand_probability_weight: Default 1. Relative weight of the sand obstacle when choosing a random obstacle.

    Returns:
        A object representing a map.
    """
    map_graph = generate_map_graph(width, height, percentage_of_connections, rng)
    tile_map_object = map_graph_to_tile_map_object(width, height, map_graph)
    add_connections_to_borders(tile_map_object, percentage_of_connections, rng)

    if obstacle_probability > 0:
        add_obstacles_to_map(
            tile_map_object,
            obstacle_probability,
            rng,
            ice_probability_weight=ice_probability_weight,
            broken_road_probability_weight=broken_road_probability_weight,
            sand_probability_weight=sand_probability_weight,
        )

    return tile_map_object


def generate_map_graph(
    width: int, height: int, percentage_of_connections: float, rng
) -> graph.Graph:
    """Generates a graph representing a map based on the provided parameters.

    Args:
        width: The width of the generated map graph in tiles.
        height: The height of the generated map graph in tiles.
        percentage_of_connections: The percentage of connections that are generated compared to all possible connection that could exist. A value of 1 lead each tile being connected to all neighbors. The start and end of the map are always connected, even if a value of 0 is chosen.
        rng: (np rng) A rng that is used for all randomness.

    Returns:
        A graph representing a map.
    """

    map_graph = graph.Graph()

    for i in range(width):
        for j in range(height):
            current_node_id = i + j * width

            if not (i == width - 1):
                map_graph.add_edge(current_node_id, current_node_id + 1, 1, True)
            if not (j == height - 1):
                map_graph.add_edge(current_node_id, current_node_id + width, 1, True)

    removable_edges = [(edge[0], edge[1]) for edge in map_graph.edges()]

    map_graph.add_edge("start", 0, 1, True)
    map_graph.add_edge("end", width * height - 1, 1, True)

    num_edges_to_keep = round(len(removable_edges) * percentage_of_connections)

    shortest_path = map_graph.breadth_first_search("start", "end")

    # remove edges until the desired number of edges is reached or no more edges can be removed (don't count the four edges that are always there: start to first node and reverse, end to last node and reverse)
    while len(map_graph.edges()) - 4 > num_edges_to_keep and len(removable_edges) > 0:

        chosen_edge = tuple(rng.choice(removable_edges))
        chosen_edge_reverse = tuple(reversed(chosen_edge))

        removable_edges.remove(chosen_edge)
        removable_edges.remove(chosen_edge_reverse)

        map_graph.del_edge(*chosen_edge)
        map_graph.del_edge(*chosen_edge_reverse)

        if all(x in shortest_path for x in chosen_edge):
            # it is not necessary to check if the two nodes of the chosen edge appear behind each other in the shortest path, if they didn't it wouldn't be a shortest path
            if map_graph.is_connected("start", "end"):
                shortest_path = map_graph.breadth_first_search("start", "end")
            else:
                map_graph.add_edge(*chosen_edge)
                map_graph.add_edge(*chosen_edge_reverse)

    return map_graph


def map_graph_to_tile_map_object(
    width: int, height: int, graph: graph.Graph
) -> MapPlan:
    """Turns a graph representing a map into a dict object representing the same map.

    Args:
        width: The width of the map in tiles.
        height: The height of the map in tiles.
        graph: The graph representing the map.

    Returns:
        The map object.
    """

    map_plan = MapPlan(width, height, [])

    for i in range(height - 1, -1, -1):
        row = []
        for j in range(width):
            tile = {}
            tile["exits"] = [0, 0, 0, 0]
            current_node_id = j + i * width
            neighboring_nodes = graph.nodes(from_node=current_node_id)

            if neighboring_nodes == None:
                continue

            if (current_node_id + width) in neighboring_nodes:  # tile to the north
                tile["exits"][0] = 1

            if (current_node_id + 1) in neighboring_nodes:  # tile to the east
                tile["exits"][1] = 1

            if (current_node_id - width) in neighboring_nodes:  # tile to the south
                tile["exits"][2] = 1

            if (current_node_id - 1) in neighboring_nodes:  # tile to the west
                tile["exits"][3] = 1

            row.append(tile)
        map_plan.tiles.append(row)

    map_plan.tiles[height - 1][0]["exits"][3] = 1  # add the start exit
    map_plan.tiles[0][width - 1]["exits"][1] = 1  # add the end exit

    return map_plan


def add_connections_to_borders(
    map: MapPlan, percentage_of_connections_to_edges: float, rng
) -> None:
    """Given a map object adds connections from the tiles next to the borders to the borders.

    Args:
        map_object: The map object that the connections will be added to.
        percentage_of_connections: The percentage of connections that are generated compared to all possible connection that could exist. A value of 1 lead each tile next to a border being connected to said border and a value of 0 leads to none being connected (except start and end).
        rng: (np rng) A rng that is used for all randomness.
    """

    width = map.width
    height = map.height

    # list of possible connections to edges as (tile_y, tile_x, direction) with direction: 0=north/top 1=east/right 2=south/bottom 3=west/left
    possible_connections_to_borders = (
        [(0, x, 0) for x in range(width)]  # connections to top edge
        + [(y, width - 1, 1) for y in range(height)]  # connections to right edge
        + [(height - 1, x, 2) for x in range(width)]  # connections to bottom edge
        + [(y, 0, 3) for y in range(height)]  # connection to left edge
    )

    possible_connections_to_borders.remove((height - 1, 0, 3))  # remove the start
    possible_connections_to_borders.remove((0, width - 1, 1))  # remove the goal

    num_connections_to_borders_to_add = round(
        len(possible_connections_to_borders) * percentage_of_connections_to_edges
    )

    for _ in range(num_connections_to_borders_to_add):
        connection_to_border_to_add = tuple(rng.choice(possible_connections_to_borders))
        possible_connections_to_borders.remove(connection_to_border_to_add)
        map.tiles[connection_to_border_to_add[0]][connection_to_border_to_add[1]][
            "exits"
        ][connection_to_border_to_add[2]] = 1


def add_obstacles_to_map(
    map: MapPlan,
    obstacle_probability: float,
    rng,
    *,
    ice_probability_weight: float = 1,
    broken_road_probability_weight: float = 1,
    sand_probability_weight: float = 1,
) -> None:
    """Given a map object adds obstacles to the tiles.

    Args:
        map_object: The map object that the obstacles will be added to.
        obstacle_probability: The probability of adding a obstacle to a tile.
        rng: (np rng) A rng that is used for all randomness.
        ice_probability_weight: Default 1. Relative weight of the ice obstacle when choosing a random obstacle.
        broken_road_probability_weight: Default 1. Relative weight of the broken road obstacle when choosing a random obstacle.
        sand_probability_weight: Default 1. Relative weight of the sand obstacle when choosing a random obstacle.
    """

    probability_weight_sum = (
        ice_probability_weight
        + broken_road_probability_weight
        + sand_probability_weight
    )

    ice_relative_probability_weight = ice_probability_weight / probability_weight_sum
    broken_road_relative_probability_weight = (
        broken_road_probability_weight / probability_weight_sum
    )
    sand_relative_probability_weight = sand_probability_weight / probability_weight_sum

    for row in range(map.height):
        for column in range(map.width):
            if (
                rng.random() < obstacle_probability
                and not str(map.tiles[row][column]["exits"]) == "[0, 0, 0, 0]"
            ):
                obstacle_type = rng.choice(
                    OBSTACLE_NAMES,
                    p=[
                        ice_relative_probability_weight,
                        broken_road_relative_probability_weight,
                        sand_relative_probability_weight,
                    ],
                )
                map.tiles[row][column]["obstacle_type"] = obstacle_type
                map.tiles[row][column]["obstacle_mask"] = rng.choice(
                    OBSTACLE_MASK_NAMES
                )
