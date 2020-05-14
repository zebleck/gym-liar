import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='Liar-v0',
    entry_point='gym_liar.envs:LiarEnv',
    nondeterministic = True,
)
