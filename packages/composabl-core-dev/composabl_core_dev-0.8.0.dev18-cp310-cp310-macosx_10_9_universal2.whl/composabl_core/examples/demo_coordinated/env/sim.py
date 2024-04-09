# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import gymnasium as gym

import composabl_core.utils.logger as logger_util
from composabl_core.agent.scenario.scenario import Scenario

logger = logger_util.get_logger(__name__)


class Sim(gym.Env):
    def __init__(self, env_init: dict = {}):
        # Define the initial values
        self.time_ticks = 0
        self.value = 0
        self.is_done = False
        self.steps = 0

        # Define the observation and action spaces
        self.observation_space = gym.spaces.Dict({
            "state1": gym.spaces.Box(low=-1e12, high=1e12),
            "time_ticks": gym.spaces.Box(low=0, high=1e12)
        })

        self.action_space = gym.spaces.Dict({
            "skill1": gym.spaces.Discrete(3),
            "skill2": gym.spaces.Discrete(3)
        })

        # Define the scenario
        self.scenario: Scenario = None

    def _get_observation(self):
        obs = {"state1": self.value, "time_ticks": self.time_ticks}
        return obs

    def reset(self):
        self.time_ticks = 0
        self.value = 0
        self.is_done = False
        self.steps = 0

        obs = self._get_observation()
        info = {}

        return obs, info

    def set_scenario(self, scenario):
        self.scenario = scenario

    def step(self, action):
        # Increase time counting
        self.time_ticks += 1
        self.steps += 1

        assert self.action_space.contains(action), f"Invalid action: {action}"

        #  Update obs with new state values (dummy function)
        obs = self._get_observation()
        reward = 0
        info = {}

        if self.steps > 10:
            self.is_done = True

        return obs, reward, self.is_done, False, info
