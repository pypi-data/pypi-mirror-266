from pymgrid.MicrogridGenerator import MicrogridGenerator
from pymgrid.convert.convert import to_modular,  to_nonmodular
import pandas as pd

mgen = MicrogridGenerator(nb_microgrid=3)
mgen.generate_microgrid()
microgrid = mgen.microgrids[2]

nonmodular = to_nonmodular(microgrid)
print(nonmodular)

mgen = MicrogridGenerator(nb_microgrid=3)
mgen.generate_microgrid()
