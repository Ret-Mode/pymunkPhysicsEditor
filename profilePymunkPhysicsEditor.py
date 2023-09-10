import cProfile
import pstats
from pstats import SortKey

import PymunkPhysicsEditor

cProfile.run('PymunkPhysicsEditor.main()', 'output.perf')
pstats.Stats('output.perf').sort_stats(SortKey.CUMULATIVE).print_stats('editorCode')