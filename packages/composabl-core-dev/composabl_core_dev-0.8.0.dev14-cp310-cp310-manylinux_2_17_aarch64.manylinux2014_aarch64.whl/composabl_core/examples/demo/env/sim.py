# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Any, Dict, SupportsFloat, Tuple

import gymnasium as gym
import numpy as np
import random

import composabl_core.utils.logger as logger_util

logger = logger_util.get_logger(__name__)

MAX_COUNTER = 10  # max 8 bit value due to MultiBinary space


class Sim(gym.Env):
    """
    The simulation environment is designed to test and demonstrate how different observation and
    action space configurations can be implemented and interacted with in RL.

    The goal of the simulation environment is to count to MAX_COUNTER as quickly as possible
    """
    def __init__(self, env_init: dict = {}):
        self.space_type = env_init.get("space_type", "discrete")
        self.counter = 0  # Initialize counter
        self.steps = 0 # keeps track of epsiode length
        # Define observation and action spaces
        if self.space_type == "discrete":
            self.observation_space = gym.spaces.Discrete(MAX_COUNTER + 1)  # 0-MAX_COUNTER (just return the counter)
            self.action_space = gym.spaces.Discrete(2)  # Increment by 1, or reset to 0
        elif self.space_type == "multidiscrete":
            self.observation_space = gym.spaces.MultiDiscrete([MAX_COUNTER + 1])
            self.action_space = gym.spaces.MultiDiscrete([2, 3])
        elif self.space_type == "multibinary":
            self.observation_space = gym.spaces.MultiBinary(7)  # Binary representation of MAX_COUNTER
            self.action_space = gym.spaces.MultiBinary(1)  # Increment or reset
        elif self.space_type == "box":
            self.observation_space = gym.spaces.Box(low=np.array([0]), high=np.array([MAX_COUNTER]), dtype=np.float32)
            self.action_space = gym.spaces.Box(low=np.array([0]), high=np.array([1]), dtype=np.float32)  # Increment by 1 or reset
        elif self.space_type == "dictionary":
            self.observation_space = gym.spaces.Dict({
                "counter": gym.spaces.Box(low=np.array([0]), high=np.array([MAX_COUNTER]), dtype=np.float32)
            })
            self.action_space = gym.spaces.Dict({
                "increment": gym.spaces.Discrete(2)  # Increment by 1, or reset to 0
            })
        elif self.space_type == "tuple":
            self.observation_space = gym.spaces.Tuple([
                gym.spaces.Discrete(10)
            ])
            self.action_space = gym.spaces.Tuple([
                gym.spaces.Discrete(2)  # Increment by 1, or reset to 0
            ])
        else:
            raise ValueError(f"Unknown space type {self.space_type}")

        # Print Debug
        print(f"Initialized Sim (action space: {self.action_space}, obs space: {self.observation_space})")


    def get_action_mask(self):
        if self.space_type == "discrete":
            mask = random.choice([np.array([0, 1]), np.array([1, 0])])
        elif self.space_type == "multidiscrete":
            mask1 = random.choice([np.array([0, 1]), np.array([1, 0])])
            mask2 = random.choice([np.array([0, 1, 1]), np.array([1, 1, 0])])
            mask = tuple([mask1, mask2])
        elif self.space_type == "multibinary":
            mask = [random.choice([0, 1])]
        elif self.space_type == "box":
            mask = [1] # can't mask box
        elif self.space_type == "dictionary":
            mask = {"increment": random.choice([np.array([0, 1]), np.array([1, 0])])}
        elif self.space_type == "tuple":
            mask = random.choice([np.array([0, 1]), np.array([1, 0])])
            mask = tuple([mask])
        return {"action_mask": mask}
    
    def step(self, action) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]:
        # Process action
        self.steps += 1
        self._process_action(action)

        # Generate observation based on space type
        obs = self._get_observation()

        # Check if goal is reached
        done = self.steps == MAX_COUNTER
        reward = 1 if done else 0  # Reward when goal is reached
        info = self.get_action_mask()

        return obs, reward, done, False, info

    def reset(self):
        self.counter = 0
        self.steps = 0

        info = self.get_action_mask()
        return self._get_observation(), info

    def _process_action(self, action):
        # 0 = increment, 1 = decrement
        value_to_add = 0

        if self.space_type == "discrete":
            value_to_add = (1 if action == 0 else -1)
        elif self.space_type == "multidiscrete":
            value_to_add = (1 if action[0] == 0 else -1)
        elif self.space_type == "multibinary":
            value_to_add = (1 if action == 0 else -1)
        elif self.space_type == "box":
            value_to_add = (1 if action[0] <= 0.5 else -1)
        elif self.space_type == "dictionary":
            value_to_add = (1 if action["increment"] == 0 else -1)
        elif self.space_type == "tuple":
            value_to_add = (1 if action[0] == 0 else -1)
        else:
            raise ValueError(f"Unknown space type {self.space_type}")

        # Update the counter but ensure it stays within the bounds
        self.counter = max(0, min(MAX_COUNTER, self.counter + value_to_add))

    def _get_observation(self):
        if self.space_type == "discrete":
            return self.counter
        elif self.space_type == "multidiscrete":
            return [self.counter]
        elif self.space_type == "multibinary":
            return np.binary_repr(self.counter, width=7)
        elif self.space_type == "box":
            return np.array([self.counter], dtype=np.float32)
        elif self.space_type == "dictionary":
            return {"counter": self.counter}
        elif self.space_type == "tuple":
            return (self.counter,)
        else:
            raise ValueError(f"Unknown space type {self.space_type}")

    def render(self, mode="human"):
        print(f"Counter: {self.counter}")
