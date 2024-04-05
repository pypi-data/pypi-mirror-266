# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import random

from composabl_core.agent.skill.skill_controller import SkillController


class ControllerExpertDict(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """
    def __init__(self):
        self.wrong_action_probability = 0.05

    async def compute_action(self, obs):
        action = 1 if random.random() < self.wrong_action_probability else 0

        return {
            "increment": action  # 0 = increment, 1 is decrement
        }

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10


class ControllerExpertBox(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """
    def __init__(self):
        self.wrong_action_probability = 0.05

    async def compute_action(self, obs):
        return [1]

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10


class ControllerExpertTuple(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """
    def __init__(self):
        self.wrong_action_probability = 0.05

    async def compute_action(self, obs):
        return [1]

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10


class ControllerExpertDiscrete(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """
    def __init__(self):
        self.wrong_action_probability = 0.05

    async def compute_action(self, obs):
        return 1

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10


class ControllerExpertMultiDiscrete(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """
    def __init__(self):
        self.wrong_action_probability = 0.05

    async def compute_action(self, obs):
        return [1, 0]

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10


class ControllerRandomDict(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """
    def __init__(self):
        pass

    async def compute_action(self, obs):
        return {
            "increment": random.randint(0, 1)  # 0 = increment, 1 is decrement
        }

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10


class ControllerRandomBox(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """
    def __init__(self):
        pass

    async def compute_action(self, obs):
        return [random.randint(0, 1)]  # 0 = increment, 1 is decrement

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10


class ControllerRandomDiscrete(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """
    def __init__(self):
        pass

    async def compute_action(self, obs):
        return random.randint(0, 1)  # 0 = increment, 1 is decrement

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10\


class ControllerRandomTuple(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """
    def __init__(self):
        pass

    async def compute_action(self, obs):
        return [random.randint(0, 1)] # 0 = increment, 1 is decrement

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10


class ControllerRandomMultiDiscrete(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """
    def __init__(self):
        pass

    async def compute_action(self, obs):
        return [random.randint(0, 1), 0] # 0 = increment, 1 is decrement

    async def transform_obs(self, obs):
        return obs

    async def filtered_observation_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_obs, action):
        return transformed_obs["counter"][0] >= 10

    async def compute_termination(self, transformed_obs, action):
        return transformed_obs["counter"][0] <= -10
