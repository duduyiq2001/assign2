import argparse
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import BinaryResource
from gem5.runtime import get_supported_isas
from gem5.simulate.simulator import Simulator
from gem5.utils.requires import requires

from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
import m5
from m5.objects import *
from Caches import *
import os
gem5_path = os.environ["GEM5"]
gem5_testprogs = os.path.join(gem5_path, "testprogs")


parser = argparse.ArgumentParser()
parser.add_argument("--prog", required=True, choices=["daxpy", "queens"])
parser.add_argument("--daxpy-N", default=100, type=int)
parser.add_argument("--queens-N", default=10, type=int)
parser.add_argument("--bp", default=None, type=str)
parser.add_argument("--bp_size", default=None, type=int)
parser.add_argument("--bp_bits", default=None, type=int)
args = parser.parse_args()
program_str = args.prog
daxpy_N = args.daxpy_N
queens_N = args.queens_N
bp = args.bp


# Get supported ISAs and unpack into a single value.
isa, = get_supported_isas()
isa_str = isa.value

# Create Processor
processor = SimpleProcessor(
    cpu_type=CPUTypes.MINOR,
    isa=isa,
    num_cores=1,
)

# Set the branch predictor
for cpu in processor.get_cores():
    if bp == "TournamentBP":
        bp_core = TournamentBP(
            localPredictorSize=args.bp_size,
            localCtrBits=args.bp_bits,
            globalPredictorSize=args.bp_size,
            globalCtrBits=args.bp_bits,
            choicePredictorSize=args.bp_size,
            choiceCtrBits=args.bp_bits
        )
        bp_core.btb.numEntries = args.bp_size
        cpu.core.branchPred = bp_core
    else:
        bp_core = LocalBP(
            localPredictorSize=args.bp_size,
            localCtrBits=args.bp_bits
        )
        bp_core.btb.numEntries = args.bp_size
        cpu.core.branchPred = bp_core

clk_freq = "1GHz"
if isa in (ISA.ARM, ISA.RISCV):
    clk_freq = "1.2GHz"


cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="64KiB",
    l1i_size="16KiB",
    4
    l2_size="256KiB",
)

# Override the cache classes
cache_hierarchy._l1d_cache_class = MyL1DCache
cache_hierarchy._l1i_cache_class = MyL1ICache
cache_hierarchy._l2_cache_class = MyL2Cache

memory = SingleChannelDDR3_1600(size="32MB")


board = SimpleBoard(
    clk_freq=clk_freq,
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)


full_program_path = os.path.join(gem5_testprogs, program_str + "_" + isa_str)
arguments = []
if program_str == "daxpy":
    arguments = [daxpy_N]
elif program_str == "queens":
    arguments = [queens_N]
board.set_se_binary_workload(
    BinaryResource(full_program_path),
    arguments=arguments,
)


simulator = Simulator(board=board)
simulator.run()
