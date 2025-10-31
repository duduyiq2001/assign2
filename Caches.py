
from gem5.components.cachehierarchies.classic.caches.l1dcache import L1DCache
from gem5.components.cachehierarchies.classic.caches.l1icache import L1ICache
from gem5.components.cachehierarchies.classic.caches.l2cache import L2Cache


class MyL1ICache(L1ICache):
    def __init__(self):
        super().__init__(size="16kB")
        self.writeback_clean = False
        self.assoc = 2
        self.tag_latency = 2
        self.data_latency = 2
        self.response_latency = 2
        self.mshrs = 4
        self.tgts_per_mshr = 20

class MyL1DCache(L1DCache):
    def __init__(self):
        super().__init__(size="64kB")
        self.writeback_clean = False
class MyL2Cache(L2Cache):
    def __init__(self):
        super().__init__(size="256kB")
        self.writeback_clean = False
        self.assoc = 8
        self.tag_latency = 20
        self.data_latency = 20
        self.response_latency = 80
        self.mshrs = 20
        self.tgts_per_mshr = 12
