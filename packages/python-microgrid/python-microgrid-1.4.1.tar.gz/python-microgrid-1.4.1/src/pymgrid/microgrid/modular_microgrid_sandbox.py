import yaml
import numpy as np

from pymgrid import Microgrid
from pymgrid.MicrogridGenerator import MicrogridGenerator

mgen = MicrogridGenerator(nb_microgrid=25)
mgen.generate_microgrid()
microgrid = mgen.microgrids[0]

from_scenario = Microgrid.from_scenario(0)

raise RuntimeError
