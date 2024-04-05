from gymnasium.envs.registration import register

from pgtg.environment import PGTGEnv

__version__ = "0.2.0"

register(id="pgtg-v1", entry_point="pgtg.environment:PGTGEnv")
