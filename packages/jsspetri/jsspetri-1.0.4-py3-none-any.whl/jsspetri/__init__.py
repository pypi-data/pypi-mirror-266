from gymnasium.envs.registration import register

# Register the 'jsspetri-mono' environment
register(
    id="jsspetri",
    entry_point="jsspetri.envs.mono.gym_env:JsspetriEnv",
    nondeterministic=False
)

# Register the 'jsspetri-multi' environment
register(
    id="jsspetri-multi",
    entry_point="jsspetri.envs.multi.gym_env:JsspetriMultiEnv",
    nondeterministic=False
)