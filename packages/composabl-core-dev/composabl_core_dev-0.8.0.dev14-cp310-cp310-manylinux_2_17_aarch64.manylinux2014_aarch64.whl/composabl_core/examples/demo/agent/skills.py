# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core.agent.scenario.scenario import Scenario
from composabl_core.agent.skill.skill import Skill
from composabl_core.examples.demo.agent import scenarios
from composabl_core.examples.demo.agent.controller import (
    ControllerExpertBox,
    ControllerExpertDict,
    ControllerExpertDiscrete,
    ControllerExpertMultiDiscrete,
    ControllerExpertTuple,
    ControllerRandomBox,
    ControllerRandomDict,
    ControllerRandomDiscrete,
    ControllerRandomMultiDiscrete,
    ControllerRandomTuple,
)
from composabl_core.examples.demo.agent.teacher import (
    Teacher,
    TeacherSpaceBox,
    TeacherSpaceDictionary,
    TeacherSpaceDiscrete,
    TeacherSpaceMultiBinary,
    TeacherSpaceMultiDiscrete,
    TeacherSpaceTuple,
)

expert_skill_controller_box = Skill("expert-controller", ControllerExpertBox)
random_skill_controller_box = Skill("random-controller", ControllerRandomBox)

expert_skill_controller_discrete = Skill("expert-controller", ControllerExpertDiscrete)
random_skill_controller_discrete = Skill("random-controller", ControllerRandomDiscrete)

expert_skill_controller_multi_discrete = Skill("expert-controller", ControllerExpertMultiDiscrete)
random_skill_controller_multi_discrete = Skill("random-controller", ControllerRandomMultiDiscrete)

expert_skill_controller_dict = Skill("expert-controller", ControllerExpertDict)
random_skill_controller_dict = Skill("random-controller", ControllerRandomDict)

expert_skill_controller_tuple = Skill("expert-controller", ControllerExpertTuple)
random_skill_controller_tuple = Skill("random-controller", ControllerRandomTuple)


target_skill_nested_scenario = Skill("teacher-skill-nested-scenario", Teacher)
target_skill_box = Skill("teacher-skill-box", TeacherSpaceBox)
target_skill_discrete = Skill("teacher-skill-discrete", TeacherSpaceDiscrete)
target_skill_multi_discrete = Skill("teacher-skill-multi-discrete", TeacherSpaceMultiDiscrete)
target_skill_multi_binary = Skill("teacher-skill-multi-binary", TeacherSpaceMultiBinary)
target_skill_dictionary = Skill("teacher-skill-dictionary", TeacherSpaceDictionary)
target_skill_tuple = Skill("teacher-skill-tuple", TeacherSpaceTuple)

target_skills = [
    target_skill_nested_scenario,
    target_skill_box,
    target_skill_discrete,
    target_skill_multi_discrete,
    target_skill_multi_binary,
    target_skill_dictionary,
    target_skill_tuple,
]

for ts in target_skills:
    for scenario_dict in scenarios:
        ts.add_scenario(Scenario(scenario_dict))

target_skill_nested_scenario.add_scenario({
    "test": "test",
    "nested": {
        "test": "test",
        "double_nested": {
            "test": "test"
        }
    }
})

skills_for_space = {
    "box": target_skill_box,
    "discrete": target_skill_discrete,
    "multidiscrete": target_skill_multi_discrete,
    "multibinary": target_skill_multi_binary,
    "dictionary": target_skill_dictionary,
    "tuple": target_skill_tuple
}
