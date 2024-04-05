import json

from pgtg import parser
from pgtg.constants import TILE_HEIGHT, TILE_WIDTH
from pgtg.map_generator import MapPlan


class EpisodeMap:
    """Class representing a map for the environment that can be modified and used for running a episode."""

    def __init__(self, map_plan: MapPlan):
        # save the original map plan to be able to later save the map to a file
        self.map_plan = map_plan

        (self.width, self.height, self._map, self.num_subgoals) = (
            parser.parse_map_object(self.map_plan)
        )

        self.tile_width = int(self.width / TILE_WIDTH)
        self.tile_height = int(self.height / TILE_HEIGHT)

        self.starters = []
        self.goals = []
        self.traffic_spawnable_positions = []
        self.car_spawners = []

        for x in range(self.width):
            for y in range(self.height):
                if self.feature_at(x, y, "start"):
                    self.starters.append((x, y))
                if any(
                    ["car_lane" in feature for feature in self.get_features_at(x, y)]
                ):
                    self.traffic_spawnable_positions.append((x, y))
                if self.feature_at(x, y, "car_spawner"):
                    self.car_spawners.append((x, y))
                if self.feature_at(x, y, "final goal"):
                    self.goals.append((x, y))

    def inside_map(self, x: int, y: int) -> bool:
        """Returns true if the position specified by the x and y coordinates is inside the map and false otherwise."""

        return not (x < 0 or y < 0 or x >= self.width or y >= self.height)

    def get_features_at(self, x: int, y: int) -> set[str]:
        """Returns a list of all features at the position specified by the x and y coordinates."""

        if x < 0 or x > self.width - 1 or y < 0 or y > self.height - 1:
            raise ValueError("coordinates are outside the map")
        return self._map[x][y]

    def set_features_at(self, x: int, y: int, features: set[str]) -> None:
        """Replaces the features at the the position specified by the x and y coordinates with the provided ones."""

        if x < 0 or x > self.width - 1 or y < 0 or y > self.height - 1:
            raise ValueError("coordinates are outside the map")
        self._map[x][y] = features

    def feature_at(self, x: int, y: int, features: str | set[str] | list[str]) -> bool:
        """Returns true if one of the specified features is present at the the position specified by the x and y coordinates and false otherwise."""

        if isinstance(features, str):
            return features in self.get_features_at(x, y)
        else:
            return not self.get_features_at(x, y).isdisjoint(features)

    def add_feature_at(self, x: int, y: int, feature: str) -> None:
        """Adds the specified feature at the the position specified by the x and y coordinates."""
        self.get_features_at(x, y).add(feature)

    def remove_feature_at(self, x: int, y: int, feature: str) -> None:
        """Removes the specified feature at the the position specified by the x and y coordinates. Doesn't raise an error if feature is not present."""

        self.get_features_at(x, y).discard(feature)

    def get_tile_view(self, x: int, y: int) -> list[list[set[str]]]:
        """Cuts out the map tile at the specified coordinates. If coordinates outside the map are chosen, cuts out the closest tile instead.

        Args:
            x: x-value of the tile
            y: y-value of the tile

        Returns:
            A cutout from the map representing the tile at the specified coordinates.
        """

        # set max and min values in case the agent has left the map
        x = max(x, 0)
        x = min(x, self.tile_width - 1)
        y = max(y, 0)
        y = min(y, self.tile_height - 1)

        # calculate the coordinates of the upper left corner of the tile.
        tile_x = x * TILE_WIDTH
        tile_y = y * TILE_HEIGHT
        # cut the row of tiles
        cut_map = self._map[tile_x : tile_x + TILE_WIDTH]
        res = []
        for row in cut_map:
            res.append(row[tile_y : tile_y + TILE_HEIGHT])
        return [
            *zip(*res)
        ]  # transpose the 2d array to match observations from before the map representation redesign

    def set_subgoals_to_used(self, x: int, y: int) -> None:
        """Marks the subgoal at the specified coordinates as used and recursively marks all directly adjacent subgoals as used as well.

        Args:
            x: x-value of the position
            y: y-value of the position
        """

        assert self.feature_at(x, y, "subgoal"), (
            "Subgoal expected but found "
            + str(self.get_features_at(x, y))
            + " instead."
        )

        self.remove_feature_at(x, y, "subgoal")
        self.add_feature_at(x, y, "used subgoal")

        # recursively replace directly adjacent subgoal parts
        if self.feature_at(x, y + 1, "subgoal"):
            self.set_subgoals_to_used(x, y + 1)

        if self.feature_at(x, y - 1, "subgoal"):
            self.set_subgoals_to_used(x, y - 1)

        if self.feature_at(x + 1, y, "subgoal"):
            self.set_subgoals_to_used(x + 1, y)

        if self.feature_at(x - 1, y, "subgoal"):
            self.set_subgoals_to_used(x - 1, y)

    def save_map(self, path: str) -> None:
        """Saves the map as a JSON file.

        Args:
            path (String): path to the file the map should be saved in.
        """

        if not path.endswith(".json"):
            path += ".json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.map_plan, f, ensure_ascii=False, indent=4)
