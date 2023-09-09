import cProfile
import pstats
from pstats import SortKey

import VehicleEditor

cProfile.run('VehicleEditor.main()', 'output.perf')
pstats.Stats('output.perf').sort_stats(SortKey.CUMULATIVE).print_stats('editorCode')