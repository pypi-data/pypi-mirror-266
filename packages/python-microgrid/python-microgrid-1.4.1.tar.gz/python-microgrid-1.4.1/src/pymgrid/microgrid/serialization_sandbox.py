
from pymgrid.envs import DiscreteMicrogridEnv
from pymgrid import Microgrid

microgrid = Microgrid.from_scenario(microgrid_number=2)
env = DiscreteMicrogridEnv.from_scenario(microgrid_number=2)
print(microgrid)