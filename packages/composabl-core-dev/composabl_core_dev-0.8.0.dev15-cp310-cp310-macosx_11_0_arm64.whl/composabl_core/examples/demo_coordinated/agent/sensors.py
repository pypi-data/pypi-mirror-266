# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core.agent.sensor import Sensor

s1 = Sensor("state1", "the counter", lambda obs: obs["state1"])
s2 = Sensor("time_ticks", "the time counter", lambda obs: obs["time_ticks"])

sensors = [s1, s2]
