# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import math
from typing import List

from composabl_core import SkillController


class Controller(SkillController):
    """
    We start at 10 reward and count down to 0 the goal is that the agent stays
    above or equal to 0 this means it learned to cound +1 each time
    """

    def __init__(self):
        self.past_obs = None
        self.counter = 10
        self.sensor_name = "counter"

    async def compute_action(self, transformed_obs, action) -> List[bool]:
        return None

    async def compute_success_criteria(self, transformed_obs, action) -> bool:
        return bool(transformed_obs[self.sensor_name] >= 10)

    async def compute_termination(self, transformed_obs, action) -> bool:
        return bool(transformed_obs[self.sensor_name] <= -10)

    async def transform_obs(self, obs, action) -> str:
        return obs

    async def transform_action(self, transformed_obs, action) -> float:
        return action

    async def filtered_observation_space(self) -> List[str]:
        return [self.sensor_name]
