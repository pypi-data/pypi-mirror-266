# ProcGrid Traffic Gym (pgtg)

A driving simulation on a grid with procedural generated maps and traffic. Compatible with the Gymnasium API standard.

### Installation

```bash
pip install pgtg
```

### Usage
The easiest way to use pgtg is to create the environment with gymnasium:
```python
import pgtg
env = gymnasium.make("pgtg-v1")
```
The package relies on ```import``` side-effects to register the environment
name so, even though the package is never explicitly used, its import is
necessary to access the environment.  

If you want to access the environment constructor directly this is also possible:
```python
from pgtg import PGTGEnv
env = PGTGEnv()
```

## Environment
ProcGrid Traffic Gym procedurally generates a map consisting of multiple preconstructed tiles or loads a map from a file. The goal is to drive from the start of the map to the end. The navigation task is not part of this environment, instead a shortest path is provided and marked on the map.  

The environment is highly customizable, see the constructor documentation for more info.

### Action Space
ProcGrid Traffic Gym has a `Discrete(9)` action space.

| Value | Meaning                   |
|-------|---------------------------|
| 0     | accelerate left and up    |
| 1     | accelerate left           |
| 2     | accelerate left and down  |
| 3     | accelerate up             |
| 4     | don't accelerate          |
| 5     | accelerate down           |
| 6     | accelerate right and up   |
| 7     | accelerate right          |
| 8     | accelerate right and down |

### Observation Space
ProcGrid Traffic Gym has a `Dict` observation space that shows the 9x9 area the agent currently is inside.
| Key | Type | Explanation |
|-----|------|-------------|
| "position" | `MultiDiscrete` | The x and y position of the agent within the observation window. |
| "velocity" | `Box` | The velocity of the agent is x and y direction. |
| "map" | `Dict` | The 9x9 are of the map the agent is currently inside. The keys are the name of the features (`"walls"`, `"goals"`, `"ice"`, `"broken road"`, `"sand"`, and `"traffic"`). Each item is a `MultiBinary` that encodes that feature as a hot one encoding. |

Most reinforcement learning implementations can't deal with `Dict` observations, thus it might be necessary to flatten the observations. This is easily doable with the `gymnasium.wrappers.FlattenObservation` wrapper:
```python
from gymnasium.wrappers import FlattenObservation
env = FlattenObservation(env)
```

### Reward
Crossing a subgoal is rewarded with `+100 / number of subgoals` as is finishing the whole map. Moving into a wall or traffic is punished with `-100` and ends the episode. Standing still or moving to a already visited position can also penalized but is not per default. The reward values for each of this can be customized.

### Render modes
| Name | Explanation |
|------|-------------|
| human | `render()` returns `None` but a pygame window showing the environment is opened automatically when `step()` is called. |
| rgb_array | `render()` returns a `np.array` representing a image. |
| pil_image| `render()` returns a `PIL.Image.Image`, useful for displaying inside jupiter notebooks. |

### Obstacles
| Name | Effect |
|------|--------|
| Ice | When driving over a square with ice, there is a chance the agent moves in a random direction instead of the expected one. |
| Sand | When driving over sand, there is a chance that the agent is slowed, as the velocity is reset to 0. |
| Broken road | When driving over broken road, there is a chance for the agent to get a flat tire. This slows the agent down, as the velocity is reset to 0 every step. A flat tire lasts until the end of the episode.|

## Version History
- v0: initial release
- v1: Sand now slows down with a customizable probability (default 20%) instead of always.