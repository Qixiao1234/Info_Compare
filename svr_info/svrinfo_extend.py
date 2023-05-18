import os
import re
import json
import math
from collections import OrderedDict

from svrinfo import Svrinfo

BIOSPAT = OrderedDict([
    ('Hyper-Threading Enabled', r'^Thread\(.*:\s*(.+?)\n'),
    ('Turbo Enabled', r'\s*Intel Turbo Boost Technology\s*= (.+?)\n'),
    ('Power & Perf Policy', None),
    ('Vt-d Enabled', r'(Directed\sI.O)'),
])


# print (Svrinfo.__get_pattern())
# from Svrinfo import __test
# print (Svrinfo._Svrinfo__test())

class Svrinfo(Svrinfo):

    def get_bios_info_ek(self):
        """parse CPU info"""
        # if self._cpu is not None:
        #     return self._cpu
        rethosts = OrderedDict(
            (k, OrderedDict.fromkeys(BIOSPAT, "")) for k in self._cmdict
        )

        for k in BIOSPAT.keys():
            if BIOSPAT[k] is None:
                continue
            self.__get_pattern(
                BIOSPAT,
                k,
                [
                    "lscpu",
                    "cpuid -1",
                    "dmesg"
                ],
                rethosts,
            )
        # transform any outputs
        for h in rethosts:
            data = rethosts[h]
            data["Hyper-Threading Enabled"] = (
                "Yes" if data["Hyper-Threading Enabled"] == "2" else "No"
            )
            data["Vt-d Enabled"] = (
                "Yes" if data["Vt-d Enabled"] == "Directed I/O" else "No"
            )

        self.__get_cpu_perfpolicy(rethosts)

        # self._cpu = rethosts
        return rethosts

    def get_cmdline(self):
        """Get cmdline"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("cmdline"):
            rethosts[host] = cmdout

        return rethosts

    def get_gccver(self):
        """Get gcc version"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("gcc --version"):
            rethosts[host] = cmdout

        return rethosts

    # add
    #     def get_MSR(self):
    #         print('=================================================')
    #         print(self._cmdict)
    #         rethosts = OrderedDict((k, []) for k in self._cmdict)
    #         for host, cmdout in self.__get_cmd_gen("Register and MSR"):
    #             rethosts[host] = cmdout
    #         print(rethosts)
    #         for host, cmdout in self.__get_cmd_gen("PKGC 0xE2[2：0]"):
    #             rethosts[host] = cmdout
    #         print(rethosts)
    #         for host, cmdout in self.__get_cmd_gen("Turbo Enable 0x199[32]"):
    #             rethosts[host] = cmdout
    #         print(rethosts)
    #         return rethosts

    def get_javaver(self):
        """Get java version"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("java -version"):
            rethosts[host] = cmdout

        return rethosts

    def get_CPU_IDLE(self):
        """Get CPU IDLE state"""

        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("cpupower idle-info"):
            rethosts[host] = cmdout

        return rethosts

