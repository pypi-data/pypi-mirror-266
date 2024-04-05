# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core.agent.skill.skill_teacher import SkillTeacher


class CartpoleTeacher(SkillTeacher):
    def __init__(self):
        pass

    async def compute_reward(self, transformed_obs, action, sim_reward):
        """
        Compute the reward
        Example Obs: {'cart_pos': 0.0034704863, 'cart_vel': -0.24383363, 'pole_theta': -0.042229883, 'pole_alpha': 0.2794808}
        """
        # Cartpole-specific reward logic, potentially based on pole angle and cart position
        pole_angle = transformed_obs["pole_theta"]  # Extracting pole angle from observation
        cart_position = transformed_obs["cart_pos"]  # Extracting cart position

        # Reward for being close to upright and center
        reward = max(0, 1 - abs(pole_angle) / 0.418) + max(0, 1 - abs(cart_position) / 2.4)

        return reward

    async def compute_action_mask(self, transformed_obs, action):
        # Cartpole might not use an action mask, so this can return None
        return None

    async def compute_success_criteria(self, transformed_obs, action):
        # Example success condition: pole angle close to vertical
        return abs(transformed_obs["pole_theta"]) < 0.05  # Less than ~3 degrees

    async def compute_termination(self, transformed_obs, action):
        # Terminates if cart out of bounds or pole falls too much
        cart_out_of_bounds = abs(transformed_obs["cart_pos"]) > 2.4
        pole_fell = abs(transformed_obs["pole_theta"]) > 0.418  # More than 24 degrees
        return cart_out_of_bounds or pole_fell

    async def transform_obs(self, obs, action):
        # For Cartpole, might just return obs directly
        return obs

    async def transform_action(self, transformed_obs, action):
        # No transformation needed for discrete action space
        return action

    async def filtered_observation_space(self):
        # Return relevant observation dimensions if necessary
        return ["cart_pos", "cart_vel", "pole_theta", "pole_alpha"]


class PoleBalanceTeacher(CartpoleTeacher):
    async def compute_reward(self, transformed_obs, action, sim_reward):
        pole_angle = abs(transformed_obs["pole_theta"])
        pole_velocity = abs(transformed_obs["pole_alpha"])

        # Higher reward for smaller angles and velocities
        return 1.0 - (pole_angle + pole_velocity) / 0.418

    async def compute_termination(self, transformed_obs, action):
        """
        For balancing the pole, we terminate early if the pole falls too much
        """
        return abs(transformed_obs["pole_theta"]) > 0.418

    async def compute_success_criteria(self, transformed_obs, action):
        """
        For balancing the pole, we consider the pole upright if it's within 3 degrees of vertical
        """
        return abs(transformed_obs["pole_theta"]) < 0.05  # Less than ~3 degrees


class CartMoveToCenterTeacher(CartpoleTeacher):
    async def compute_reward(self, transformed_obs, action, sim_reward):
        cart_position = abs(transformed_obs["cart_pos"])

        # Reward inversely proportional to distance from center
        return 1.0 - cart_position / 2.4

    async def compute_termination(self, transformed_obs, action):
        """
        For moving to center, we terminate early if it's too far from the center
        """
        return abs(transformed_obs["cart_pos"]) > 2.4

    async def compute_success_criteria(self, transformed_obs, action):
        """
        For moving to center, we consider the cart at the center if it's within 0.1 units
        """
        return abs(transformed_obs["cart_pos"]) < 0.1


class BalanceTeacher(SkillTeacher):
    def __init__(self):
        self.steps = 0
        self.obs_history = {
            "cart_pos": [],
            "cart_vel": [],
            "pole_theta": [],
            "pole_alpha": [],
        }
        pass

    async def compute_reward(self, transformed_obs, action, sim_reward):
        """
        Compute the reward
        Example Obs: {'cart_pos': 0.0034704863, 'cart_vel': -0.24383363, 'pole_theta': -0.042229883, 'pole_alpha': 0.2794808}
        """
        self.steps += 1
        for k, v in transformed_obs.items():
            self.obs_history[k].append(v)
        # Cartpole-specific reward logic, potentially based on pole angle and cart position
        pole_angle = transformed_obs["pole_theta"]  # Extracting pole angle from observation
        cart_position = transformed_obs["cart_pos"]  # Extracting cart position

        # Reward for being close to upright and center
        reward = max(0, 1 - abs(pole_angle) / 0.418) + max(0, 1 - abs(cart_position) / 2.4)

        return sim_reward

    async def compute_action_mask(self, transformed_obs, action):
        # Cartpole might not use an action mask, so this can return None
        return None

    async def compute_success_criteria(self, transformed_obs, action):
        return False

    async def compute_termination(self, transformed_obs, action):
        return False

    async def transform_obs(self, obs, action):
        # For Cartpole, might just return obs directly
        return obs

    async def transform_action(self, transformed_obs, action):
        # No transformation needed for discrete action space
        return action

    async def filtered_observation_space(self):
        # Return relevant observation dimensions if necessary
        return ["cart_pos", "cart_vel", "pole_theta", "pole_alpha"]