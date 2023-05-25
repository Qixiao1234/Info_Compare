import re
import json
import math
from collections import OrderedDict

CPU_FAM = [6]
CPU_SKL = [85]
CPU_BDW = [61, 71, 79, 86]

SYSDPAT = OrderedDict(
    [
        ("Manufacturer", r"^\s*Manufacturer:\s*(.+?)\n"),
        ("Product Name", r"^\s*Product Name:\s*(.+?)\n"),
        ("BIOS Version", r"^\s*Version:\s*(.+?)\n"),
        ("OS", r"^PRETTY_NAME=\"(.+?)\""),
        ("Kernel", r"^Linux \S+ (\S+)"),
        ("Microcode", r"^microcode.*:\s*(.+?)\n"),
    ]
)

SYSPAT = OrderedDict(
    [("Host Time", r"^(.*UTC\s*[0-9]*)\n$"), ("Host Name", r"^Linux (\S+) \S+")]
)

PREF = [(4, "DCU HW"), (8, "DCU IP"), (1, "L2 HW"), (2, "L2 Adj.")]
# add
CPUPAT = OrderedDict(
    [
        ("Model Name", r"^[Mm]odel name.*:\s*(.+?)\n"),
        ("Sockets", r"^Socket\(.*:\s*(.+?)\n"),
        ("Core(s) per socket", r"^Core\(s\) per socket.*:\s*(.+?)\n"),
        ("Hyper-Threading Enabled", r"^Thread\(.*:\s*(.+?)\n"),
        ("Total CPU(s)", r"^CPU\(.*:\s*(.+?)\n"),
        ("NUMA Nodes", r"^NUMA node\(.*:\s*(.+?)\n"),
        ("NUMA cpulist", None),
        ("L1d Cache", r"^L1d cache.*:\s*(.+?)\n"),
        ("L1i Cache", r"^L1i cache.*:\s*(.+?)\n"),
        ("L2 Cache", r"^L2 cache.*:\s*(.+?)\n"),
        ("L3 Cache", r"^L3 cache.*:\s*(.+?)\n"),
        ("Prefetchers Enabled", None),
        ("Intel Turbo Boost Enabled", r"\s*Intel Turbo Boost Technology\s*= (.+?)\n"),
        ("Power & Perf Policy", None),
        ("CPU Freq Driver", r"^CPU Freq Driver:\s*(.+?)\n"),
        ("CPU Freq Governor", r"^CPU Freq Governor:\s*(.+?)\n"),
        ("Current CPU Freq MHz", r"^CPU MHz:\s*([0-9]*).*\n"),
        ("AVX2 Available", r"\s*AVX2: advanced vector extensions 2\s*= (.+?)\n"),
        (
            "AVX512 Available",
            r"\s*AVX512F: AVX-512 foundation instructions\s*= (.+?)\n",
        ),
        ("AVX512 Test", r"AVX512TEST: (\w*)\n"),
		("CPUidle driver", r"^CPUidle driver: (.+?)\n"),
		("Number of idle states", r"^Number of idle states: (.+?)\n"),
		("Available idle states", r"^Available idle states: (.+?)\n"),
		("Flags/Description", r"^Flags/Description: (.+?)\n"),
		("hardware limits", r"hardware limits: (.+?)\n"),
		("available cpufreq governors", r"available cpufreq governors: (.+?)\n"),
		("current policy", r"current policy: (.+?)\n"),
    ]
)

MEMPAT = OrderedDict(
    [
        ("MemTotal", r"^MemTotal:\s*(.+?)\n"),
        ("MemFree", r"^MemFree:\s*(.+?)\n"),
        ("MemAvailable", r"^MemAvailable:\s*(.+?)\n"),
        ("Buffers", r"^Buffers:\s*(.+?)\n"),
        ("Cached", r"^Cached:\s*(.+?)\n"),
        ("HugePages_Total", r"^HugePages_Total:\s*(.+?)\n"),
        ("Hugepagesize", r"^Hugepagesize:\s*(.+?)\n"),
    ]
)

# add
MSRPAT = OrderedDict(
    [
        ("PKGC", r"^PKGC:\s*(.+?)\n"),
        ("Turbo Enable", r"^Turbo Enable:\s*(.+?)\n"),
        ("EPB", r"^EPB:\s*(.+?)\n"),
        ("PC1E", r"^PC1E:\s*(.+?)\n"),
        ("Dynamic Switching", r"^Dynamic Switching:\s*(.+?)\n"),
        ("EE Policy Control", r"^EE Policy Control:\s*(.+?)\n"),
        ("System Agent PM Control", r"^System Agent PM Control:\s*(.+?)\n"),
        ("Uncore Min Freq Limits", r"^Uncore Min Freq Limits:\s*(.+?)\n"),
        ("Uncore Max Freq Limits", r"^Uncore Max Freq Limits:\s*(.+?)\n"),
        ("HWP Enable", r"^HWP Enable:\s*(.+?)\n"),
        ("EPP", r"^EPP:\s*(.+?)\n"),
        ("Max Frequency", r"^Max Frequency:\s*(.+?)\n"),
        ("Min Frequency", r"^Min Frequency:\s*(.+?)\n"),
        ("Energy Efficient Turbo", r"^Energy Efficient Turbo:\s*(.+?)\n"),
		
		("SMI_Count", r"^SMI_Count:\s*(.+?)\n"),
		("MSR_PPIN", r"^MSR_PPIN:\s*(.+?)\n"),
		("IA32_BIOS_Sign_ID", r"^IA32_BIOS_Sign_ID:\s*(.+?)\n"),
		("Platform_Info", r"^Platform_Info:\s*(.+?)\n"),
		("MSR_PKG_CST_Config_Control", r"^MSR_PKG_CST_Config_Control:\s*(.+?)\n"),
		("IA32_Perf_Status", r"^IA32_Perf_Status:\s*(.+?)\n"),
		("IA32_Perf_Ctl", r"^IA32_Perf_Ctl:\s*(.+?)\n"),
		("IA32_Therm_Status", r"^IA32_Therm_Status:\s*(.+?)\n"),
		("IA32_MISC_Enable", r"^IA32_MISC_Enable:\s*(.+?)\n"),
		("Prefetch_CTL", r"^Prefetch_CTL:\s*(.+?)\n"),
		("IA32_Engergy_Perf_Bias", r"^IA32_Engergy_Perf_Bias:\s*(.+?)\n"),
		("IA32_Package_Therm_Status", r"^IA32_Package_Therm_Status:\s*(.+?)\n"),
		("MSR_Power_CTL", r"^MSR_Power_CTL:\s*(.+?)\n"),
		("MSR_Core_C6_Residency", r"^MSR_Core_C6_Residency:\s*(.+?)\n"),
		("Uncore_Ratio_Limit", r"^Uncore_Ratio_Limit:\s*(.+?)\n"),
		("Uncore_Perf_status", r"^Uncore_Perf_status:\s*(.+?)\n"),
        ("IA_Perf_Limit_Reason", r"^IA_Perf_Limit_Reason:\s*(.+?)\n"),
		("IA32_HWP_Request", r"^IA32_HWP_Request:\s*(.+?)\n"),
		("0x80000694 0xb1", r"^0x80000694 0xb1:\s*(.+?)\n")
    ]
)

# add
PERF_PLIMIT_PAT = OrderedDict(
    [
        ("PERF PLIMIT ENABLE", r"^PERF PLIMIT ENABLE:\s*(.+?)\n"),
        ("PERF PLIMIT THRESHOLD", r"^PERF PLIMIT THRESHOLD:\s*(.+?)\n"),
        ("PERF PLIMIT CLIP", r"^PERF PLIMIT CLIP:\s*(.+?)\n"),
        ("PERF PLIMIT DIFFERENTIAL", r"^PERF PLIMIT DIFFERENTIAL:\s*(.+?)\n"),
    ]
)

DIMMPAT = OrderedDict(
    [
        ("Manufacturer", r"^\tManufacturer:\s*(.+?)\n"),
        ("Part", r"^\tPart Number:\s*(.+?)\s*\n"),
        ("Serial", r"^\tSerial Number:\s*(.+?)\s*\n"),
        ("Size", r"^\tSize:\s*(.+?)\n"),
        ("Type", r"^\tType:\s*(.+?)\n"),
        ("Detail", r"^\tType Detail:\s*(.+?)\n"),
        ("Speed", r"^\tSpeed:\s*(.+?)\n"),
        ("ConfiguredSpeed", r"^\tConfigured Clock Speed:\s*(.+?)\n"),
        ("BankLocator", r"^\tBank Locator: (.*)\n"),
        ("Locator", r"^\tLocator: (.*)\n"),
        ("Rank", r"^\tRank: (.*)\n"),
    ]
)

SYSSTS = OrderedDict(
    [
        ("Last Power Event", r"^Last Power Event\s*: (.+?)\n"),
        ("Power Overload", r"^Power Overload\s*: (.+?)\n"),
        ("Main Power Fault", r"^Main Power Fault\s*: (.+?)\n"),
        ("Power Restore Policy", r"^Power Restore Policy\s*: (.+?)\n"),
        ("Drive Fault", r"^Drive Fault\s*: (.+?)\n"),
        ("Cooling/Fan Fault", r"^Cooling/Fan Fault\s*: (.+?)\n"),
        ("System Time", None),
    ]
)


class Svrinfo:
    def __init__(self, sifile):
        self._cmdict = self.__parse_inp(sifile)
        self._cpu = None

    def __parse_inp(self, filename):
        """parse input file into cmds and output lines from cmd execution"""
        cmdict = None
        cmd = None
        host = None
        with open(filename, "r") as file:
            cmdict = OrderedDict()
            for line in file:
                if line.startswith("--------------- Host"):
                    try:
                        host = re.search(".*Host (.+?) --", line).group(1)
                    except AttributeError:
                        raise SystemExit("Hostname not found: " + line)
                    cmdict[host] = {}
                    cmd = None
                elif line.startswith("> "):
                    cmd = line[2:].split(":")[0]
                    cmdict[host][cmd] = []
                elif host and cmd:
                    cmdict[host][cmd].append(line)
        if cmdict is None or len(cmdict) == 0:
            raise RuntimeError("Unable to parse input file")
        return cmdict

    def __get_cmd_gen(self, cmd_match):
        """create a generator for matching cmd for each host"""
        return (
            (host, cmdout)
            for host in self._cmdict.keys()
            for cmdkey, cmdout in self._cmdict[host].items()
            if cmd_match in cmdkey
        )

    def __get_cmd(self, host, cmd_match):
        """return matching cmd output for given host"""
        for curhost, cmdout in self.__get_cmd_gen(cmd_match):
            if host == curhost:
                return cmdout
        return None

    def __get_pattern(self, pat, patkey, cmdmatchlist, rethosts):
        for cmdmatch in cmdmatchlist:
            for host, cmdout in self.__get_cmd_gen(cmdmatch):
                if rethosts[host][patkey] != "":
                    continue
                lines = cmdout
                # Use only BIOS and System info from dmidecode
                if "dmidecode" in cmdmatch:
                    try:
                        lines = (
                                self.__get_dmitype("0")[host][0]
                                + self.__get_dmitype("1")[host][0]
                        )
                    except IndexError:
                        lines = ""
                for line in lines:
                    try:
                        rethosts[host][patkey] = re.search(pat[patkey], line).group(1)
                        break
                    except AttributeError:
                        pass

    def __get_node_cpulist(self, rethosts):
        for h, c in self.__get_cmd_gen("lscpu"):
            clist = []
            for line in c:
                try:
                    clist.append(
                        re.search(r"^NUMA node[0-9] CPU\(.*:\s*(.+?)\n", line).group(1)
                    )
                except AttributeError:
                    pass
            rethosts[h]["NUMA cpulist"] = " :: ".join(clist)

    def get_cpu_family(self):
        hostfm = OrderedDict((k, {"fam": "", "model": ""}) for k in self._cmdict)
        self.__get_pattern({"fam": r"^CPU family:\s*(.+?)\n"}, "fam", ["lscpu"], hostfm)
        self.__get_pattern({"model": r"^Model:\s*(.+?)\n"}, "model", ["lscpu"], hostfm)
        remove = []
        for host in hostfm:
            if host.startswith("Reference_Intel"):
                remove.append(host)
                continue
            try:
                family = int(hostfm[host]["fam"])
                model = int(hostfm[host]["model"])
                if family not in CPU_FAM or (
                        model not in CPU_BDW and model not in CPU_SKL
                ):
                    raise Exception("unrecognized CPU")
            except:
                remove.append(host)
                continue
        for host in remove:
            del hostfm[host]
        return hostfm

    # Takes the MSR hex value and converts them into the correct order decimal/integer format array
    def __convert_hex(self, msr, decimal):
        hexvals = re.findall("[0-9a-fA-F][0-9a-fA-F]", msr)
        decvals = []
        for i in hexvals:
            val = "0x" + i
            if decimal:
                val = int(val, 16) / float(10)
            else:
                val = int(val, 16)
            decvals.append(val)
        decvals.reverse()
        return decvals

    def __get_msr_hex_str(self, line):
        result = re.search("^([0-9a-fA-F]+)", line)
        if result:
            return result.group(1)
        else:
            return None

    def __get_cores_per_socket(self, target_host):
        for host, cmdout in self.__get_cmd_gen("lscpu"):
            if host != target_host:
                continue
            for line in cmdout:
                r = re.search(r"^Core\(s\) per socket.*:\s*(.+?)\n", line)
                if r and len(r.groups()) == 1:
                    return int(r.group(1))
        return None

    def __get_frequency_count(self, target_host):
        core_count = self.__get_cores_per_socket(target_host)
        cc_to_fc = {
            2: 1,
            4: 2,
            6: 3,
            8: 3,
            10: 3,
            12: 4,
            14: 4,
            16: 5,
            18: 6,
            20: 6,
            22: 7,
            24: 7,
            26: 8,
            28: 8,
        }
        frequency_count = cc_to_fc[core_count]  # raises exception if out of range
        return frequency_count

    def get_cpu_frequencies(self):
        hostfm = self.get_cpu_family()
        # Frequency MSR
        hosts_freq = OrderedDict()
        for h, c in self.__get_cmd_gen("rdmsr 0x1ad"):
            if h in hostfm:
                msr = self.__get_msr_hex_str(c[0])
                if msr:
                    freqvals = self.__convert_hex(msr, True)
                    # attempt to trim list to actual number of cores
                    try:
                        freq_count = self.__get_frequency_count(h)
                        freqvals = freqvals[:freq_count]
                    except:
                        pass
                    hosts_freq[h] = freqvals
        # Core MSR
        hosts_cores = OrderedDict()
        for h, c in self.__get_cmd_gen("rdmsr 0x1ae"):
            if h in hostfm:
                msr = self.__get_msr_hex_str(c[0])
                if msr:
                    corevals = self.__convert_hex(msr, False)
                    # attempt to trim list to actual number of cores
                    try:
                        freq_count = self.__get_frequency_count(h)
                        # On BDX, we get '28' repeated for each core val, so we override below
                        if corevals and corevals[0] == corevals[1]:
                            corevals[0] = 2
                            corevals[1] = 4
                            corevals[2] = 8
                            corevals[3] = 12
                            corevals[4] = 16
                            corevals[5] = 20
                            corevals[6] = 24
                            corevals[7] = 28
                            corevals[freq_count - 1] = self.__get_cores_per_socket(h)
                        corevals = corevals[:freq_count]
                    except:
                        pass
                    hosts_cores[h] = corevals
        return hosts_cores, hosts_freq

    def __get_cpu_prefetchers(self, rethosts):
        for h, c in self.__get_cmd_gen("rdmsr 0x1a4"):
            clist = []
            hex_str = self.__get_msr_hex_str(c[0])
            if hex_str:
                clist = [x[1] for x in PREF if not x[0] & int(hex_str, 16)]
            if clist:
                rethosts[h]["Prefetchers Enabled"] = ", ".join(clist)
            else:
                rethosts[h]["Prefetchers Enabled"] = "Unknown"

    def __get_cpu_perfpolicy(self, rethosts):
        for h, c in self.__get_cmd_gen("rdmsr 0x1b0"):
            pol = "Unknown"
            hex_str = self.__get_msr_hex_str(c[0])
            if hex_str:
                p = int(hex_str, 16)
                if p < 7:
                    pol = "Performance"
                elif p > 10:
                    pol = "Power"
                else:
                    pol = "Balanced"
            rethosts[h]["Power & Perf Policy"] = pol

    def __get_cpu_ppin(self, rethosts):
        for h, c in self.__get_cmd_gen("rdmsr 0x4f"):
            ppin = "Unknown"
            hex_str = self.__get_msr_hex_str(c[0])
            if hex_str:
                ppin = hex_str
            rethosts[h]["PPIN (CPU0)"] = ppin

    def get_cpu(self):
        """parse CPU info"""
        if self._cpu is not None:
            return self._cpu
        rethosts = OrderedDict(
            (k, OrderedDict.fromkeys(CPUPAT, "")) for k in self._cmdict
        )
        for k in CPUPAT.keys():
            if CPUPAT[k] is None:
                continue
            self.__get_pattern(
                CPUPAT,
                k,
                [
                    "lscpu",
                    "cpu_freq_drv_pol",
                    "cpuid -1",
                    "/proc/cpuinfo",
                    "avx512test",
					"idle_info",
					"frequency_info",
                ],
                rethosts,
            )
        # transform any outputs
        for h in rethosts:
            data = rethosts[h]
            if data["Hyper-Threading Enabled"]:
                data["Hyper-Threading Enabled"] = (
                    "Yes" if data["Hyper-Threading Enabled"] == "2" else "No"
                )
            if data["Intel Turbo Boost Enabled"]:
                data["Intel Turbo Boost Enabled"] = (
                    "Yes" if data["Intel Turbo Boost Enabled"] == "true" else "No"
                )
            if data["AVX2 Available"]:
                data["AVX2 Available"] = "Yes" if data["AVX2 Available"] == "true" else "No"
            if data["AVX512 Available"]:
                data["AVX512 Available"] = (
                    "Yes" if data["AVX512 Available"] == "true" else "No"
                )
        self.__get_node_cpulist(rethosts)
        self.__get_cpu_prefetchers(rethosts)
        self.__get_cpu_perfpolicy(rethosts)
        self.__get_cpu_ppin(rethosts)
        self._cpu = rethosts
        return rethosts

    def get_sysd(self):
        """parse sys detailed info"""
        rethosts = OrderedDict(
            (k, OrderedDict.fromkeys(SYSDPAT, "")) for k in self._cmdict
        )
        for k in SYSDPAT.keys():
            if SYSDPAT[k] is None:
                continue
            self.__get_pattern(
                SYSDPAT, k, ["dmidecode", "release", "uname", "/proc/cpuinfo"], rethosts
            )
        return rethosts

    def get_security_vuln(self):
        rethosts = OrderedDict((k, None) for k in self._cmdict)
        cmdexists = False
        for host, cmdout in self.__get_cmd_gen("spectre-meltdown-checker"):
            cmdexists = True
            rethosts[host] = OrderedDict()
            for line in cmdout:
                r = re.search(r"(CVE-\d+-\d+): (.+)", line)
                if r and len(r.groups()) == 2:
                    rethosts[host][r.group(1)] = r.group(2)
        if not cmdexists:
            return None
        return rethosts

    def get_calc_freq(self):
        """parse calcfreq output
        CalcFreq v1.0
        P1 freq = 3092 MHz
        1-core turbo    3082 MHz
        2-core turbo    3295 MHz
        """
        rethosts = OrderedDict((k, None) for k in self._cmdict)
        cmdexists = False
        for host, cmdout in self.__get_cmd_gen("Measure Turbo"):
            cmdexists = True
            rethosts[host] = OrderedDict()
            for line in cmdout:
                r = re.search(r"^(\d+)-core turbo\s+(\d+) MHz", line)
                if r and len(r.groups()) == 2:
                    rethosts[host][r.group(1)] = r.group(2)
        if not cmdexists:
            return None
        return rethosts

    def get_mem(self):
        """parse mem detailed info"""
        rethosts = OrderedDict(
            (k, OrderedDict.fromkeys(MEMPAT, "")) for k in self._cmdict
        )
        # print('++++++++++++++++++++++++')
        # print(self._cmdict)
        # print('++++++++++++++++++++++++')
        # print(rethosts)
        for k in MEMPAT.keys():
            if MEMPAT[k] is None:
                continue
            self.__get_pattern(MEMPAT, k, ["meminfo"], rethosts)
        # print("000000000000000000000000000000000000000000000000000000000")
        # print(rethosts)

        return rethosts

    # add
    def get_msr(self):
        """parse msr detailed info"""
        rethosts = OrderedDict(
            (k, OrderedDict.fromkeys(MSRPAT, "")) for k in self._cmdict
        )
        # print('++++++++++++++++++++++++')
        # print(self._cmdict)
        # print('++++++++++++++++++++++++')
        # print(rethosts)
        # print(self._cmdict.keys())
        # print('++++++++++++++++++++++++')
        # print(self._cmdict['dut'].items())
        for k in MSRPAT.keys():
            if MSRPAT[k] is None:
                continue
            self.__get_pattern(MSRPAT, k, ["msrinfo"], rethosts)
        # print("000000000000000000000000000000000000000000000000000000000")
        #
        # print(rethosts)
        return rethosts

    # add
    def get_PERF_PLIMIT(self):
        """parse msr detailed info"""
        rethosts = OrderedDict(
            (k, OrderedDict.fromkeys(PERF_PLIMIT_PAT, "")) for k in self._cmdict
        )
        # print('++++++++++++++++++++++++')
        # print(self._cmdict)
        # print('++++++++++++++++++++++++')
        # print(rethosts)
        # print(self._cmdict.keys())
        # print('++++++++++++++++++++++++')
        # print(self._cmdict['dut'].items())
        for k in PERF_PLIMIT_PAT.keys():
            if PERF_PLIMIT_PAT[k] is None:
                continue
            self.__get_pattern(PERF_PLIMIT_PAT, k, ["PERF PLIMIT INFO"], rethosts)
        # print("000000000000000000000000000000000000000000000000000000000")
        #
        # print(rethosts)
        return rethosts

    def get_sys(self):
        """parse sys info"""
        rethosts = OrderedDict(
            (k, OrderedDict.fromkeys(SYSPAT, "")) for k in self._cmdict
        )
        for k in SYSPAT.keys():
            if SYSPAT[k] is None:
                continue
            self.__get_pattern(SYSPAT, k, ["uname", "date -u"], rethosts)

        return rethosts

    def get_sensors(self):
        """Get System Sensors """
        rethosts = OrderedDict((k, None) for k in self._cmdict)
        cmdexists = False
        for host, cmdout in self.__get_cmd_gen("ipmitool sdr list full"):
            cmdexists = True
            rethosts[host] = OrderedDict()
            for line in cmdout:
                s = re.split(r"\s*\|\s*", line)
                if len(s) == 3:
                    rethosts[host][s[0]] = " - ".join(s[1:3])
        if not cmdexists:
            return None
        return rethosts

    def get_chassis_status(self):
        """Get ipmitool chassis status"""
        rethosts = OrderedDict(
            (k, OrderedDict.fromkeys(SYSSTS, "")) for k in self._cmdict
        )
        for k in SYSSTS.keys():
            if SYSSTS[k] is None:
                continue
            self.__get_pattern(SYSSTS, k, ["ipmitool chassis status"], rethosts)
        # transform any outputs
        for host, cmdout in self.__get_cmd_gen("ipmitool sel time get"):
            for line in cmdout:
                if len(line) > 10:
                    rethosts[host]["System Time"] = line.strip()
        return rethosts

    def __get_dmitype(self, dmitype):
        """Get dmidecode for given dmitype"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("dmidecode"):
            start = False
            index = 0
            ret = []
            for line in cmdout:
                if start and line.startswith("Handle "):
                    start = False
                    index += 1
                if "DMI type " + dmitype + "," in line:
                    ret.insert(index, [])
                    start = True
                if start:
                    ret[index].append(line)
            rethosts[host] = ret
        return rethosts

    def __get_dimm_socket_slot(self, bloc, loc):
        """ return socket and slot numbers starting at zero """
        r = re.search(r"CPU([0-9])_([A-Z])([0-9])", loc)
        if r:
            return (int(r.group(1)), int(r.group(3)))

        r = re.search(r"CPU([0-9])_MC._DIMM_([A-Z])([0-9])", loc)
        if r:
            return (int(r.group(1)), int(r.group(3)))

        r = re.search(r"NODE ([0-9]) CHANNEL ([0-9]) DIMM ([0-9])", bloc)
        if r:
            return (int(r.group(1)), int(r.group(3)))

        r = re.search(r"P([0-9])_Node([0-9])_Channel([0-9])_Dimm([0-9])", bloc)
        if r:
            return (int(r.group(1)), int(r.group(4)))

        r = re.search(r"_Node([0-9])_Channel([0-9])_Dimm([0-9])", bloc)
        if r:
            return (int(r.group(1)), int(r.group(3)))

        r = re.search(r"CPU([0-9])_DIMM_([A-Z])([0-9])", loc)
        if r:
            return (int(r.group(1)) - 1, int(r.group(3)) - 1)

        if loc.startswith("DIMM_"):
            r = re.search(r"DIMM_([A-Z])([0-9])", loc)
            if r and len(r.groups()) == 2:
                rs = re.search(r"NODE ([0-9])", bloc)
                if rs and len(rs.groups()) == 1:
                    return (int(rs.group(1)) - 1, int(r.group(2)) - 1)

        return None

    def __get_dimms_hpe(
            self,
            dimms_txt,
            num_sockets,
            dimms_per_socket,
            channels_per_socket,
            slots_per_channel,
    ):
        if slots_per_channel != 2:
            return []
        ret = []
        for dimm_txt in dimms_txt:
            dimminfo = OrderedDict.fromkeys(DIMMPAT, "")
            for k in dimminfo:
                for line in dimm_txt:
                    try:
                        dimminfo[k] = re.search(DIMMPAT[k], line).group(1)
                    except AttributeError:
                        pass
            # as seen on 2 socket HPE systems...2 slots per channel
            # Locator field has these: PROC 1 DIMM 1, PROC 1 DIMM 2, etc...
            # DIMM/slot numbering on board follows logic shown below
            if not dimminfo["BankLocator"].startswith("Not Specified"):
                return []
            r = re.search(r"PROC ([0-9]) DIMM ([0-9]*)", dimminfo["Locator"])
            if not r:
                return []
            dimminfo["Socket"] = int(r.group(1)) - 1
            dimm_num = int(r.group(2))
            dimminfo["Channel"] = (dimm_num - 1) // slots_per_channel
            dimminfo["Slot"] = (
                0
                if (dimm_num < channels_per_socket and dimm_num % 2)
                   or (dimm_num > channels_per_socket and not dimm_num % 2)
                else 1
            )
            ret.append(dimminfo)
        return ret

    def __get_dimms_dell(
            self,
            dimms_txt,
            num_sockets,
            dimms_per_socket,
            channels_per_socket,
            slots_per_channel,
    ):
        ret = []
        for dimm_txt in dimms_txt:
            dimminfo = OrderedDict.fromkeys(DIMMPAT, "")
            for k in dimminfo:
                for line in dimm_txt:
                    try:
                        dimminfo[k] = re.search(DIMMPAT[k], line).group(1)
                    except AttributeError:
                        pass
            # as seen on 2 socket Dell systems...
            # "Bank Locator" for all DIMMs is "Not Specified" and "Locator" is A1-A12 and B1-B12.
            # A1 and A7 are channel 0, A2 and A8 are channel 1, etc.
            if not dimminfo["BankLocator"].startswith("Not Specified"):
                return []
            r = re.search(r"([AB])(.*)", dimminfo["Locator"])
            if not r:
                return []
            alpha_id = r.group(1)
            numeric_id = int(r.group(2))
            dimminfo["Socket"] = 0 if alpha_id == "A" else 1
            dimminfo["Slot"] = 0 if numeric_id <= channels_per_socket else 1
            channel = (
                numeric_id - 1
                if numeric_id <= channels_per_socket
                else numeric_id - (channels_per_socket + 1)
            )
            dimminfo["Channel"] = channel
            ret.append(dimminfo)
        return ret

    def __get_dimms_other(self, cmdout, numsockets, dpers, numch, numsl):
        ret = []
        ps = -1
        dindex = 0
        sindex = -1
        c = 0
        s = 0
        sl = 0
        for dimm in cmdout:
            dimminfo = OrderedDict.fromkeys(DIMMPAT, "")
            try:
                if dindex % dpers == 0:
                    sindex = sindex + 1
            except ZeroDivisionError:
                pass
            for k in dimminfo:
                for line in dimm:
                    try:
                        dimminfo[k] = re.search(DIMMPAT[k], line).group(1)
                    except AttributeError:
                        pass
            r = self.__get_dimm_socket_slot(dimminfo["BankLocator"], dimminfo["Locator"])
            if r:
                s, sl = r
            else:
                s = sindex
                try:
                    sl = dindex % numsl
                except ZeroDivisionError:
                    sl = 0
            if s > ps:
                c = 0
            if ps == s and sl == 0:
                c = c + 1
            ps = s
            dimminfo["Socket"] = s
            dimminfo["Channel"] = c
            dimminfo["Slot"] = sl
            ret.append(dimminfo)
            dindex = dindex + 1
        return ret

    def get_dimms(self):
        """Get DIMM topology"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        # print("1111111111111111111111111rethosts")
        # print(rethosts)
        hostfam = OrderedDict((k, {"fam": ""}) for k in self._cmdict)
        # print("1111111111111111111111111hostfam")
        # print(hostfam)
        self.__get_pattern({"fam": r"^Model:\s*(.+?)\n"}, "fam", ["lscpu"], hostfam)
        hostmfg = OrderedDict((k, {"mfg": ""}) for k in self._cmdict)
        # print("1111111111111111111111111hostmfg")
        # print(hostmfg)
        self.__get_pattern(
            {"mfg": r"^\s*Vendor:\s*(.+?)\n"}, "mfg", ["dmidecode"], hostmfg
        )
        for host, cmdout in self.__get_dmitype("17").items():
            # print("1111111111111111111111111cmdout")
            # print(cmdout)
            if host.startswith("Reference_Intel"):
                continue
            numsockets = int(self.get_cpu()[host]["Sockets"])
            numdimms = len(cmdout)
            dpers = numdimms / numsockets
            if hostfam[host]["fam"] == "85":
                numch = 6
            else:
                numch = 4
            numsl = int(numdimms / (numsockets * numch))
            ret = []
            if "Dell" in hostmfg[host]["mfg"]:
                ret = self.__get_dimms_dell(cmdout, numsockets, dpers, numch, numsl)
            elif "HPE" in hostmfg[host]["mfg"]:
                ret = self.__get_dimms_hpe(cmdout, numsockets, dpers, numch, numsl)
            if not ret:
                ret = self.__get_dimms_other(cmdout, numsockets, dpers, numch, numsl)
            rethosts[host] = ret
        # print("1111111111111111111111111rethosts")
        # print(rethosts)
        return rethosts

    def get_net(self):
        """Get net info"""
        netkey = OrderedDict(
            [
                ("Name", []),
                ("Model", []),
                ("Speed", []),
                ("Link", []),
                ("Bus", []),
                ("Driver", []),
                ("Firmware", []),
                ("MAC Address", []),
            ]
        )
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("lshw"):
            ret = OrderedDict((k, []) for k in netkey)
            for line in cmdout:
                try:
                    srch = re.search(r"^pci.*? (\S+)\s+network\s+(\S.*?)\n", line)
                    ret["Name"].append(srch.group(1))
                    ret["Model"].append(srch.group(2))
                    eth = self.__get_cmd(host, "ethtool " + srch.group(1))
                    if eth is None:
                        return rethosts
                    for ethl in eth:
                        try:
                            ret["Speed"].append(
                                re.search(r"^\tSpeed:\s*(.+?)\n", ethl).group(1)
                            )
                        except AttributeError:
                            pass
                    for ethl in eth:
                        try:
                            ret["Link"].append(
                                re.search(r"^\tLink detected:\s*(.+?)\n", ethl).group(1)
                            )
                        except AttributeError:
                            pass
                    ethi = self.__get_cmd(host, "ethtool -i " + srch.group(1))
                    for ethl in ethi:
                        try:
                            ret["Bus"].append(
                                re.search(r"^bus-info:\s*(.+?)\n", ethl).group(1)
                            )
                        except AttributeError:
                            pass
                    for ethl in ethi:
                        try:
                            ret["Driver"].append(
                                re.search(r"^driver:\s*(.+?)\n", ethl).group(1)
                            )
                        except AttributeError:
                            pass
                    for ethl in ethi:
                        try:
                            ret["Firmware"].append(
                                re.search(r"^firmware-version:\s*(.+?)\n", ethl).group(
                                    1
                                )
                            )
                        except AttributeError:
                            pass
                    mac = self.__get_cmd(
                        host, "cat /sys/class/net/%s/address" % srch.group(1)
                    )
                    if mac:
                        ret["MAC Address"].append(mac[0])
                except AttributeError:
                    pass
            rethosts[host] = ret
        return rethosts

    def get_loadlat(self):
        """Get Loaded Latency for memory"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("Loaded Lat"):
            for line in cmdout:
                try:
                    rethosts[host].append(
                        re.search(
                            r"\s*?([0-9]*)\t\s*([0-9]*?)\..*\t\s*([0-9]*?)\.", line
                        ).groups()
                    )
                except AttributeError:
                    pass
        return rethosts

    def __get_turbo_val(self, turbodata):
        varr = []
        v = None
        thead = ["Package", "CPU", "Core"]
        for x in turbodata:
            vals = re.split(r"\s+", x)

            if any(m in vals[0] for m in thead):
                vald = vals[:]
                continue
            if "stress-ng" not in vals[0] and "-" in vals[0]:
                try:
                    t = vals[vald.index("PkgWatt")]
                except ValueError:
                    t = ""
                try:
                    v = (vals[vald.index("Bzy_MHz")], t)
                except ValueError:
                    v = None
            if "completed" in x:
                if not v:
                    return "", "", ""
                varr.append(v)
        if not varr:
            return "", "", ""
        return varr[0][0] + " MHz", varr[1][0] + " MHz", varr[1][1] + " Watts"

    def __get_stressng_val(self, data, name, index):
        for line in data:
            if "] " + name in line:
                try:
                    return re.split(r"\s+", line)[index][:-3]
                except IndexError:
                    break
        return None

    def __geomean(self, iterable):
        return math.exp(math.fsum(math.log(val) for val in iterable) / len(iterable))

    def __get_stressng_cpu_val(self, data):
        vals = []
        for line in data:
            tokens = line.split()
            if len(tokens) == 2:
                try:
                    vals.append(float(tokens[1]))
                except ValueError:
                    # couldn't convert token to float
                    pass
        return self.__geomean(vals)

    def __del_empty_keys(self, keys, rethosts):
        delkey = []
        for k in keys:
            found = False
            for h in rethosts:
                if rethosts[h][k]:
                    found = True
                    break
            if not found:
                delkey.append(k)

        for k in delkey:
            for h in rethosts:
                rethosts[h].pop(k)
        return rethosts

    def get_health(self):
        """Get health check macro perf"""
        hltkey = OrderedDict(
            [
                ("stressng_cpu", ""),
                ("stressng_vm", ""),
                ("stressng_cache", ""),
                ("mem_peak_bw", ""),
                ("mem_lat", ""),
                ("fio_disk", ""),
                ("iperf3", ""),
                ("turbo_peak", ""),
                ("turbo", ""),
                ("turbo_tdp", ""),
            ]
        )
        rethosts = OrderedDict(
            (k, OrderedDict.fromkeys(hltkey, "")) for k in self._cmdict
        )
        for host, cmdout in self.__get_cmd_gen("CPU Turbo"):
            (
                rethosts[host]["turbo_peak"],
                rethosts[host]["turbo"],
                rethosts[host]["turbo_tdp"],
            ) = self.__get_turbo_val(cmdout)
        for host, cmdout in self.__get_cmd_gen("stress-ng cpu methods"):
            val = self.__get_stressng_cpu_val(cmdout)
            if val:
                rethosts[host]["stressng_cpu"] = str(int(val)) + " ops/s"
        for host, cmdout in self.__get_cmd_gen("stress-ng --vm"):
            val = self.__get_stressng_val(cmdout, "vm", 8)
            if val:
                rethosts[host]["stressng_vm"] = val + " ops/s"
        for host, cmdout in self.__get_cmd_gen("stress-ng --tsearch"):
            val = self.__get_stressng_val(cmdout, "tsearch", 8)
            if val:
                rethosts[host]["stressng_cache"] = val + " ops/s"
        for host, cmdout in self.__get_cmd_gen("fio"):
            for line in cmdout:
                if "read: IOPS" in line:
                    try:
                        rethosts[host]["fio_disk"] = (
                                re.split(r"[=,]", line)[1] + " iops"
                        )
                    except IndexError:
                        pass
        for host, cmdout in self.__get_cmd_gen("iperf3"):
            for line in cmdout:
                if "receiver" in line:
                    try:
                        rethosts[host]["iperf3"] = " ".join(re.split(r"\s+", line)[6:8])
                    except IndexError:
                        pass
        for host, arr in self.get_loadlat().items():
            rethosts[host]["mem_peak_bw"] = arr[0][2] + " MB/s" if arr else ""
            rethosts[host]["mem_lat"] = arr[-1][1] + " ns" if arr else ""

        return self.__del_empty_keys(hltkey, rethosts)

    def get_block_devices(self):
        """Get storage device information as a single block of text"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("lsblk -o"):
            rethosts[host] = cmdout
        return rethosts

    def get_block_devices_raw(self):
        """Get storage device information as a list of dictionaries"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("lsblk -r"):
            rethosts[host] = []
            for idx, line in enumerate(cmdout):
                vals = line.strip().split(" ")
                if idx == 0:
                    headers = vals
                elif len(vals) == len(headers):
                    device = {}
                    for header_idx, col_header in enumerate(headers):
                        device[col_header] = vals[header_idx]
                    rethosts[host].append(device)
        return rethosts

    def get_disk_usage(self):
        """Get disk usage"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("df -h"):
            rethosts[host] = cmdout
        return rethosts

    def get_disk_usage_for_host(self, host):
        """Get disk usage for a specific host"""
        return self.__get_cmd(host, "df -h")

    def __parse_bandwidth_matrix(self, cmdout):
        """
        Parse output from mlc --bandwidth_matrix
        Return: list of tuples: (node_a, {a: bandwidth, b: bandwidth, c: band...})
        """
        rows = []
        for line in cmdout:
            match = re.search(r"^\s+(\d)\s+(\d.*)", line)
            if match:
                bwdict = {}
                for idx, bw in enumerate(match.group(2).split()):
                    bwdict[idx] = bw
                rows.append((match.group(1), bwdict))
        return rows

    def get_mlc_bandwidth(self):
        """Get MLC bandwidth"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("MLC Bandwidth"):
            rethosts[host] = self.__parse_bandwidth_matrix(cmdout)
        return rethosts

    def get_processes(self):
        """Get snapshot of currently running processes"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("ps -eo"):
            rethosts[host] = cmdout
        return rethosts

    def get_system_event_log(self):
        """Get system event log"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("ipmitool sel elist"):
            rethosts[host] = cmdout
        return rethosts
