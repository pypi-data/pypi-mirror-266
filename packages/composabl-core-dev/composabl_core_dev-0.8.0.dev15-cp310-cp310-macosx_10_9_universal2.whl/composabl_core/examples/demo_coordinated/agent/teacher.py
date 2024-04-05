# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


from composabl_core.agent.skill.skill_teacher import SkillTeacher


class IncrementTeacher(SkillTeacher):
    def __init__(self):
        self.past_obs = None
        self.counter = 0

    async def compute_reward(self, transformed_obs, action, sim_reward):
        self.counter += 1
        return 1

    async def compute_action_mask(self, transformed_obs, action):
        return None

    async def compute_success_criteria(self, transformed_obs, action):
        # keep the episodes short to make testing quicker
        return self.counter > 5

    async def compute_termination(self, transformed_obs, action):
        return False

    async def transform_obs(self, obs, action):
        return obs

    async def transform_action(self, transformed_obs, action):
        return action

    async def filtered_observation_space(self):
        return ["state1", "time_counter"]
