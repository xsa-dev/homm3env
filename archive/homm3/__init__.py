from gym.envs.registration import register

register(
    id='homm3-v0',
    entry_point='homm3.envs:Homm3Env',
)
