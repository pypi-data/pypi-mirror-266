import copy
from collections import OrderedDict
from typing import Any, SupportsFloat

import gymnasium as gym
import numpy as np
import numpy.typing as npt
import pygame
from gymnasium import spaces
from PIL.Image import Image

from pgtg import graphic
from pgtg.constants import ACTIONS_TO_ACCELERATION, TILE_HEIGHT, TILE_WIDTH
from pgtg.map import EpisodeMap
from pgtg.map_generator import generate_map
from pgtg.parser import json_file_to_map_plan


def _round(x):
    return int(np.floor(x + 0.5))


class PGTGEnv(gym.Env):
    """Class representing the modular racetrack environment."""

    metadata = {"render_modes": ["human", "rgb_array", "pil_image"], "render_fps": 4}

    def __init__(
        self,
        map_path: str | None = None,
        *,
        random_map_width: int = 4,
        random_map_height: int = 4,
        random_map_percentage_of_connections: float = 0.5,
        random_map_obstacle_probability: float = 0.0,
        random_map_ice_probability_weight: float = 1,
        random_map_broken_road_probability_weight: float = 1,
        random_map_sand_probability_weight: float = 1,
        render_mode: str | None = None,
        sum_subgoals_reward: int = 100,
        final_goal_bonus: int = 0,
        crash_penalty: int = 100,
        standing_still_penalty: int = 0,
        already_visited_position_penalty: int = 0,
        ice_probability: float = 0.1,
        street_damage_probability: float = 0.1,
        sand_probability: float = 0.2,
        traffic_density: float = 0.0,
        ignore_traffic_collisions: bool = False,
    ):
        """initializes an object of the class with the given arguments.

        Args:
            map_name: Default None. Path to map file, either absolute or relative to the current working directory. If it is None a random map is generated instead.
            random_map_width: Default 4. Width of the random map.
            random_map_height: Default 4. Height of the random map.
            random_map_percentage_of_connections: Default 0.5. Percentage of connections between tiles that will be kept while generating the random map.
            random_map_obstacle_probability: Default 0.0. Probability that a tile receives an obstacle while generating the random map.
            random_map_ice_probability_weight: Default 1. Relative weight of the ice obstacle when generating the random map.
            random_map_broken_road_probability_weight: Default 1. Relative weight of the broken_road obstacle when generating the random map.
            random_map_sand_probability_weight: Default 1. Relative weight of the sand obstacle when generating the random map.
            render_mode: Default None. What kind of output render() generates. "human" results in no output by render() but automatic displaying during step().
            sum_subgoals_reward: Default 100. The sum of all subgoal rewards. Gets split evenly among all subgoals.
            final_goal_bonus: Default 0. Bonus for the final goal that gets added to the subgoal reward.
            crash_penalty: Default 100. Penalty for driving into a wall or out of the map. The value will get negated so a positive value should be used.
            standing_still_penalty: Default 0. Penalty for not moving. Gets applied every step. The value will get negated so a positive value should be used.
            already_visited_position_penalty: Default 0. Penalty for moving to a position that was visited before. Gets applied every step for the final position of that step. Standing still does not result in penalty. The value will get negated so a positive value should be used.
            ice_probability: Default 0.1. Probability of the ice effect happening when the agent drives over it.
            street_damage_probability: Default  0.1. Probability of the broken road effect happening when the agent drives over it.
            sand_probability: Default 0.2. Probability of the sand effect happening when the agent drives over it.
            traffic_density: Default 0.0. The density of the traffic as fraction of the number of traffic cars and the number of positions where traffic could be. For a value of 0 no traffic is generated.
            ignore_traffic_collisions: Default False. If true collisions with traffic are ignored. For testing purposes.
        """

        # There are 8 different directions to accelerate into and the option to stand still.
        self.action_space = spaces.Discrete(9)

        # The agent sees the position in the current tile, its velocity and the map tile.
        self.observation_space = spaces.Dict(
            {
                "position": spaces.MultiDiscrete(
                    [TILE_WIDTH, TILE_HEIGHT], dtype=np.int32
                ),
                "velocity": spaces.Box(low=-99, high=99, shape=(2,), dtype=np.int32),
                "map": spaces.Dict(
                    {
                        "walls": spaces.MultiBinary((TILE_WIDTH, TILE_HEIGHT)),
                        "goals": spaces.MultiBinary((TILE_WIDTH, TILE_HEIGHT)),
                        "ice": spaces.MultiBinary((TILE_WIDTH, TILE_HEIGHT)),
                        "broken road": spaces.MultiBinary((TILE_WIDTH, TILE_HEIGHT)),
                        "sand": spaces.MultiBinary((TILE_WIDTH, TILE_HEIGHT)),
                        "traffic": spaces.MultiBinary((TILE_WIDTH, TILE_HEIGHT)),
                    }
                ),
            }
        )

        self.render_mode = render_mode
        self.reward_range = (-np.inf, np.inf)

        self.map_path = map_path
        self.map_plan = None

        self.random_map_width = random_map_width
        self.random_map_height = random_map_height
        self.random_map_percentage_of_connections = random_map_percentage_of_connections
        self.random_map_obstacle_probability = random_map_obstacle_probability
        self.random_map_ice_probability_weight = random_map_ice_probability_weight
        self.random_map_broken_road_probability_weight = (
            random_map_broken_road_probability_weight
        )
        self.random_map_sand_probability_weight = random_map_sand_probability_weight

        self.sum_subgoals_reward = sum_subgoals_reward  # the sum of all subgoal rewards, the individual subgoal reward is all_subgoals_reward / # of subgoals
        self.final_goal_bonus = final_goal_bonus
        self.crash_penalty = crash_penalty
        self.standing_still_penalty = standing_still_penalty
        self.already_visited_position_penalty = already_visited_position_penalty

        self.ice_probability = ice_probability
        self.street_damage_probability = street_damage_probability
        self.sand_probability = sand_probability
        self.traffic_density = traffic_density

        self.ignore_traffic_collisions = ignore_traffic_collisions

        self.window_size = 720
        self.window = None
        self.clock = None

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[OrderedDict, dict[str, Any]]:
        """Resets the environment. Must be used before starting a episode.

        Returns:
            observation: One element from within the observation space.
            info: Additional information about the state of the environment. Analogous to the info returned by step().
        """
        super().reset(seed=seed)

        # define one random number generator for each random element
        (
            self.map_rng,
            self.car_rng,
            self.ice_rng,
            self.broken_road_rng,
            self.sand_rng,
        ) = self.np_random.spawn(5)

        if (
            not self.map_path == None
        ):  # if a map_path is provided load the map from that path
            if self.map_plan == None:  # only load the file on the first reset
                self.map_plan = json_file_to_map_plan(self.map_path)
            self.map = EpisodeMap(self.map_plan)
        else:
            random_generated_map_object = generate_map(
                self.random_map_width,
                self.random_map_height,
                self.random_map_percentage_of_connections,
                self.map_rng,
                obstacle_probability=self.random_map_obstacle_probability,
                ice_probability_weight=self.random_map_ice_probability_weight,
                broken_road_probability_weight=self.random_map_broken_road_probability_weight,
                sand_probability_weight=self.random_map_sand_probability_weight,
            )
            self.map = EpisodeMap(random_generated_map_object)

        self.individual_subgoal_reward = (
            self.sum_subgoals_reward / self.map.num_subgoals
        )

        self.position = np.array(self.map_rng.choice(self.map.starters))

        self.velocity = np.array([0, 0])

        self.terminated = False
        self.truncated = False
        self.flat_tire = False

        self.positions_path = [list(self.position)]
        self.tile_path = [list(self.position)]
        self.noise_path = []

        self.cars = []
        self._next_car_id = 0

        if self.traffic_density > 0:
            self._create_initial_traffic()

        return (self.get_observation(), self.get_info())

    def _decompose_velocity(
        self, velocity: npt.NDArray | None = None
    ) -> list[npt.NDArray | None]:
        """Decomposes the velocity to all intermediate steps of length 1.

        Args:
            velocity: The velocity to decompose. If None, current velocity is used.

        Returns:
            The list of the individual steps.
        """

        if velocity is None:
            velocity = self.velocity

        dx = velocity[0]
        dy = velocity[1]

        # first compute how the complete velocity change accumulates over time steps
        # trivial case:
        if dx == 0 and dy == 0:
            return []

        res = []
        if dx == 0:
            # each possible y value
            m = np.sign(dy)  # evaluates to 1 or -1, dependent on dy>0 or dy<0
            for i in range(1, np.abs(dy) + 1):
                res.append((0, i * m))
        elif dy == 0:
            m = np.sign(dx)  # evaluates to 1 or -1, dependent of dx>0 or dx<0
            for i in range(1, np.abs(dx) + 1):
                res.append((i * m, 0))
        elif np.abs(dx) >= np.abs(dy):
            m_y = dy / np.abs(dx)
            m_x = np.sign(dx)
            for i in range(1, np.abs(dx) + 1):
                act_x = int(i * m_x)
                act_y = int(_round(i * m_y))
                res.append((act_x, act_y))
        elif np.abs(dx) < np.abs(dy):
            m_x = dx / np.abs(dy)
            m_y = np.sign(dy)
            for i in range(1, np.abs(dy) + 1):
                act_y = int(i * m_y)
                act_x = int(_round(i * m_x))
                res.append((act_x, act_y))

        pre = np.array([0, 0])

        # now deconstruct these changes into single steps by subtracting the velocity already applied
        for i, vel in enumerate(res):
            tmp = np.array(vel)
            vel = tmp - pre
            res[i] = vel
            pre = tmp

        return res

    def generate_frame(
        self,
        hide_positions: bool = False,
    ) -> Image:
        """Generates a image showing the current state of the environment.

        Args:
            hide_positions: Default False. Whether or not to hide the positions of the agent.

        Returns:
            The generated image.
        """

        pic = graphic.create_map(self, show_path=(not hide_positions))

        return pic

    def render(self) -> Image | npt.NDArray | None:
        """Potentially returns a rendered representation of the game according to the render mode.

        Returns:
            The rendered representation of the game. If the render mode is "human" or None, None is returned.
        """

        match self.render_mode:
            case None:
                return None
            case "human":
                return None
            case "rgb_array":
                return np.transpose(
                    np.asarray(self.generate_frame().convert("RGB")), axes=(1, 0, 2)
                )
            case "pil_image":
                return self.generate_frame()
            case _:
                raise Exception("the selected render_mode is not supported")

    def _render_frame_for_human(self) -> None:
        """Renders the current state of the environment in a window."""

        if self.window is None:
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (
                    self.window_size * (self.map.tile_width / self.map.tile_height),
                    self.window_size,
                )
            )
            pygame.display.set_caption("PGTG")

        if self.clock is None:
            self.clock = pygame.time.Clock()

        pil_image = self.generate_frame()

        pygame_image = pygame.image.fromstring(
            pil_image.tobytes(), pil_image.size, pil_image.mode  # type: ignore
        ).convert()

        pygame_image = pygame.transform.scale(
            pygame_image,
            (
                self.window_size * (pil_image.size[0] / pil_image.size[1]),
                self.window_size,
            ),
        )

        self.window.blit(pygame_image, pygame_image.get_rect())
        pygame.event.pump()
        pygame.display.update()

        # add a delay to keep the framerate stable
        self.clock.tick(self.metadata["render_fps"])

    def _create_initial_traffic(self) -> None:
        """Creates a number of cars defined by the traffic density."""

        initial_car_positions = self.car_rng.choice(
            self.map.traffic_spawnable_positions,
            size=int(len(self.map.traffic_spawnable_positions) * self.traffic_density),
            replace=False,
        )

        initial_car_positions = [
            tuple(initial_car_position)
            for initial_car_position in initial_car_positions
        ]

        for initial_car_position in initial_car_positions:
            routes = [
                feature.split()[1]
                for feature in self.map.get_features_at(*initial_car_position)
                if "car_lane" in feature and "all" not in feature
            ]

            # Because the features are a set, their order once converted to a list can vary, even with the same seed. Sorting the list makes the environment deterministic again.
            routes.sort()

            assert (
                len(routes) > 0
            ), "a car was spawned on a field where no car lane was found"

            self.cars.append(
                {
                    "id": self._next_car_id,
                    "position": initial_car_position,
                    "route": self.car_rng.choice(routes),
                }
            )

            self._next_car_id += 1

    def _move_car(self, car: dict[str, Any]) -> dict[str, Any] | None:
        """Moves a car to a new position if possible.

        Args:
            car: The car to move.

        Returns:
            The moved car. If there are no possible movements, None is returned.
        """

        x, y = car["position"]
        possible_directions = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
        possible_types = [
            "up",
            "down",
            "left",
            "right",
        ]

        for possible_position, type in zip(possible_directions, possible_types):
            if not self.map.inside_map(*possible_position):
                continue
                # ignore possible positions outside the map

            square_lanes = [
                feature
                for feature in self.map.get_features_at(*possible_position)
                if "car_lane" in feature
            ]

            lanes_for_all = [lane for lane in square_lanes if "all" in lane]
            if len(lanes_for_all) > 0 and type in lanes_for_all[0]:
                possible_routes = [
                    lane.split()[1] for lane in square_lanes if lane.split()[1] != "all"
                ]

                # Because the features are a set, their order once converted to a list can vary, even with the same seed. Sorting the list makes the environment deterministic again.
                possible_routes.sort()

                car["position"] = possible_position
                car["route"] = self.car_rng.choice(possible_routes)
                return car

            else:
                for lane in square_lanes:
                    if car["route"] != None and car["route"] in lane and type in lane:

                        car["position"] = possible_position
                        return car

    def _spawn_new_car(self) -> dict[str, Any]:
        """Creates a new car and returns it. It still has to be stored.

        Returns:
            The newly created car.
        """

        position = tuple(self.car_rng.choice(self.map.car_spawners))
        routes = [
            feature.split()[1]
            for feature in self.map.get_features_at(*position)
            if "car_lane" in feature and "all" not in feature
        ]

        # Because the features are a set, their order once converted to a list can vary, even with the same seed. Sorting the list makes the environment deterministic again.
        routes.sort()

        new_car = {
            "id": self._next_car_id,
            "position": position,
            "route": self.car_rng.choice(routes),
        }
        self._next_car_id += 1

        return new_car

    def step(
        self, action: int
    ) -> tuple[OrderedDict, SupportsFloat, bool, bool, dict[str, Any]]:
        """Center piece of this class. Performs the given action and returns the results.

        Args:
            action: The action to perform.

        Returns:
            observation: One element from within the observation space.
            reward: The reward for the action.
            terminated flag: Whether or not the episode has ended.
            truncated flag: Whether or not the episode has been truncated.
            info: Additional information about the state of the environment. Analogous to the info returned by reset().
        """

        # check whether the game is already done
        if self.terminated or self.truncated:
            raise RuntimeError("Already done, step has no further effect")

        # translate the action id to the acceleration
        acceleration = np.array(ACTIONS_TO_ACCELERATION[action])

        # cars move first
        new_cars = []
        for car in self.cars:
            moved_car = self._move_car(car)
            if moved_car != None:
                new_cars.append(moved_car)
            else:
                # the old car is effectively deleted because it is not added to new_cars
                # instead a new car is spawned
                new_cars.append(self._spawn_new_car())
        self.cars = new_cars

        # set start variables
        reward = 0
        current_position: npt.NDArray = copy.copy(self.position)

        # handle the velocity
        self.velocity = self.velocity + acceleration

        decomposed_velocity: list[npt.NDArray | None] = self._decompose_velocity()
        # a "stand still" check to also check the final tile of the step
        decomposed_velocity.append(None)

        # process the single steps
        while decomposed_velocity:
            velocity_part = decomposed_velocity.pop(0)

            current_position_x, current_position_y = current_position

            # case outside map, wall, or traffic
            if (
                not self.map.inside_map(current_position_x, current_position_y)
                or self.map.feature_at(current_position_x, current_position_y, "wall")
                or (
                    not self.ignore_traffic_collisions
                    and tuple(current_position)
                    in [car["position"] for car in self.cars]
                )
            ):
                reward -= self.crash_penalty
                self.terminated = True
                break

            # case goal
            if self.map.feature_at(
                current_position_x, current_position_y, "final goal"
            ):
                reward += self.individual_subgoal_reward + self.final_goal_bonus
                self.terminated = True
                break

            # case subgoal
            if self.map.feature_at(current_position_x, current_position_y, "subgoal"):
                reward += self.individual_subgoal_reward
                self.map.set_subgoals_to_used(current_position_x, current_position_y)

            # if the last step -> only checking for goal and wall, skip the rest
            if velocity_part is None:
                continue

            # case ice
            if (
                self.map.feature_at(current_position_x, current_position_y, "ice")
                and self.ice_rng.random() < self.ice_probability
            ):
                # pick a random action
                ice_action = self.ice_rng.choice(list(range(9)))
                ice_velocity = np.array(ACTIONS_TO_ACCELERATION[ice_action])
                velocity_part = ice_velocity
                self.noise_path.append(list(current_position))

            # case road_break
            if (
                self.map.feature_at(
                    current_position_x, current_position_y, "broken road"
                )
                and self.broken_road_rng.random() < self.street_damage_probability
            ):
                self.flat_tire = True
                self.noise_path.append(list(current_position))

            # case sand
            if (
                self.map.feature_at(current_position_x, current_position_y, "sand")
                and self.sand_rng.random() < self.sand_probability
            ):
                self.noise_path.append(list(current_position))
                current_position += velocity_part
                self.tile_path.append(list(current_position))
                self.velocity = np.array([0, 0])
                break

            current_position += velocity_part
            self.tile_path.append(list(current_position))

        # if there is a flat tire, the velocity is set to zero after each step.
        if self.flat_tire:
            self.velocity = np.array([0, 0])

        # apply penalty for moving to a already visited position
        if (
            self.already_visited_position_penalty != 0
            and not np.array_equal(acceleration, np.array([0, 0]))
            and any(
                [
                    np.array_equal(current_position, position_in_path)
                    for position_in_path in self.positions_path
                ]
            )
        ):
            reward -= self.already_visited_position_penalty

        # keep track of old and new position
        old_position = self.position
        self.position = current_position
        self.positions_path.append(list(self.position))

        if (
            self.standing_still_penalty != 0
            and np.array_equal(acceleration, np.array([0, 0]))
            and np.array_equal(old_position, current_position)
        ):
            reward -= self.standing_still_penalty

        if self.render_mode == "human":
            self._render_frame_for_human()

        # actually, the state is defined through pos and velocity and the distances are only features
        # for reasons of simpler implementation, the features here are returned together with the state
        return (
            self.get_observation(),
            reward,
            self.terminated,
            self.truncated,
            self.get_info(),
        )

    def light_step(
        self, action: int
    ) -> tuple[OrderedDict, SupportsFloat, bool, bool, dict[str, Any]]:
        """Copies the environment and executes a single step on it. The original environment remains unchanged.

        Args:
            action: The action to perform.

        Returns:
            observation: One element from within the observation space.
            reward: The reward for the action.
            terminated flag: Whether or not the episode has ended.
            truncated flag: Whether or not the episode has been truncated.
            info: Additional information about the state of the environment. Analogous to the info returned by reset().
        """

        env_copy = copy.deepcopy(self)
        return env_copy.step(action)

    def set_to_state(self, state: dict[str, Any]) -> tuple[OrderedDict, dict[str, Any]]:
        """Sets the environment to a given state.

        This function exists for easily making multiple recordings of a agents behavior starting from the same state.
        Setting two environments to the same state and choosing the same actions will NOT result in the same state afterwards, because the random number generators are not synchronized.

        Args:
            state: The state to set the environment to.

        Returns:
            observation: One element from within the observation space.
            info: Additional information about the state of the environment.
        """

        self.position[0] = state["x"]  # self.position[0] is the x coordinate
        self.position[1] = state["y"]  # self.position[1] is the y coordinate
        self.velocity[0] = state["x_velocity"]  # self.velocity[0] is the x velocity
        self.velocity[1] = state["y_velocity"]  # self.velocity[1] is the y velocity
        self.flat_tire = state["flat_tire"]

        self.cars = []
        if state["cars"] != None and len(state["cars"]) > 0:
            for car in state["cars"]:
                self.cars.append(
                    {
                        "id": car["id"],
                        "position": (car["x"], car["y"]),
                        "route": car["route"],
                    }
                )
            self._next_car_id = self.cars[-1]["id"] + 1

        return (self.get_observation(), self.get_info())

    def get_observation(self) -> OrderedDict[str, Any]:
        """Returns the current observation visible to the agent.

        Returns:
            A element from within the observation space.
        """

        tile_x = int(self.position[0] / TILE_WIDTH)
        tile_y = int(self.position[1] / TILE_HEIGHT)

        view = self.map.get_tile_view(tile_x, tile_y)

        map = OrderedDict(
            {
                "walls": self.translate_view_to_one_hot_encoding(view, ["wall"]),
                "goals": self.translate_view_to_one_hot_encoding(
                    view, ["subgoal", "final goal"]
                ),
                "ice": self.translate_view_to_one_hot_encoding(view, ["ice"]),
                "broken road": self.translate_view_to_one_hot_encoding(
                    view, ["broken road"]
                ),
                "sand": self.translate_view_to_one_hot_encoding(view, ["sand"]),
                "traffic": [],
            }
        )

        traffic = np.array(
            [[0] * len(view[0]) for _ in range(len(view))]
        )  # creates a (# columns in view) x (# rows in view) 2d array filled with 0

        for car in self.cars:
            if (
                tile_x * TILE_WIDTH
                <= car["position"][0]  # car[0] is the car's x position
                < (tile_x + 1) * TILE_WIDTH
                and tile_y * TILE_HEIGHT
                <= car["position"][1]  # car[1] is the car's y position
                < (tile_y + 1) * TILE_HEIGHT
            ):
                traffic[car["position"][1] - tile_y * TILE_HEIGHT][
                    car["position"][0] - tile_x * TILE_WIDTH
                ] = 1  # x and y are switched on purpose to match observations from before the map representation redesign

        map["traffic"] = traffic

        position_in_tile_x = max(0, min(8, self.position[0] - (TILE_WIDTH * tile_x)))
        position_in_tile_y = max(0, min(8, self.position[1] - (TILE_HEIGHT * tile_y)))

        observation = OrderedDict(
            {
                "position": np.array([position_in_tile_x, position_in_tile_y]),
                "velocity": np.array(
                    [self.velocity[1], self.velocity[0]]
                ),  # x and y are switched on purpose to match observations from before the map representation redesign
                "map": map,
            }
        )

        return observation

    def translate_view_to_one_hot_encoding(
        self, view: list[list[set[str]]], characters_to_match: list[str]
    ) -> npt.NDArray:
        """Translates the 2D list of sets of the map into the hot one representation for one feature.

        Args:
            view: The part of the map to be translated
            characters_to_match: List of characters that represent this feature.

        Returns:
            The hot one encoding for the specified feature.
        """

        res = []
        for row in view:
            cur = []
            for tile in row:
                if not tile.isdisjoint(characters_to_match):
                    cur.append(1)
                else:
                    cur.append(0)
            res.append(cur)
        return np.array(res)

    def get_info(self) -> dict[str, Any]:
        """Returns additional information about the state of the environment."""

        state = {
            "x": self.position[0],
            "y": self.position[1],
            "x_velocity": self.velocity[0],
            "y_velocity": self.velocity[1],
            "flat_tire": self.flat_tire,
            "cars": [],
        }
        for car in self.cars:
            state["cars"].append(
                {
                    "id": car["id"],
                    "x": car["position"][0],
                    "y": car["position"][1],
                    "route": car["route"],
                }
            )

        return state

    def applicable_actions(self) -> list[int]:
        """Returns list of applicable actions. For this environment it is always the same unless the episode is over.

        Returns:
            A list of applicable actions.
        """

        if not (self.terminated or self.truncated):
            return list(range(9))
        else:
            return []
