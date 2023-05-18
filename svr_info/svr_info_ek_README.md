# svr_info_ek User Guide

## Table of Contents
- [Introduction](#introduction)
- [Intended Audience](#intended-audience)
- [Prerequisite](#prerequisite)
    - [OS requirement](#os-requirement)
    - [Package requirement](#package-requirement)
    - [Usage](#usage) 
- [Execution](#execution)
    - [[Config] Choose testing case](#config-choose-testing-case)
    - [Prepare the needed packages](#prepare-the-needed-packages)
    - [Start Testing](#start-testing)
- [How to Scale for more tests](#how-to-scale-for-more-tests)
- [Option](#option)
    - [[Select testing] Server Conformance test](#select-testing-server-conformance-test)
    - [[Select testing] PCIE Topology Dump](#select-testing-pcie-topology-dump)
- [Legal](#legal)

## Introduction
For integrate current [svr_info](https://soco.intel.com/groups/svrinfo) project to DPG tool kit and develop for more usages.
Currently this project provides Conformance test and PCIE topology info dump. 

## Intended Audience
Internal Intel Colleague

## Prerequisite
### OS requirement
Below lists currently validated environment

| OS environment | Remark |
| :---        | :---        |
| Ubuntu 18.04 | python 3.6.8 |
| Ubuntu 16.04 | python 3.6 |

### Package requirement
```bash
    # python3 environment & "root" access
    $ pip3 install openpyxl
```

### Usage
```bash
    usage: server_info.py [-h] [-p] [-i INPUT] [-c COMPARE] [-o OUTPUT]

    svr_info_ek

    optional arguments:
    -h, --help            show this help message and exit
    -p, --prepare         To prepare the needed packages, recommand to execute
                            first
    -i INPUT, --input INPUT
                            Input board_info.txt
    -c COMPARE, --compare COMPARE
                            Input another board_info.txt for comparison
    -o OUTPUT, --output OUTPUT
                            Enter the output excel report path
```

## Execution
### [Config] Choose testing case
At conformance test, user can customize the testing cases.
```bash
    $ cd svr_info_ek
    $ vim svr_info.yml

    # To add/remove the case
    svr_info_list:
        - 'Host Name and Time'
        - 'System Details'
        - 'CPU Details'
        - 'BIOS Details'
        - 'Memory Details'
        - 'Memory Topology for hosts: dut.'
        - 'Memory Bandwidth -vs- Latency Performance Chart :'
        - 'Network Details'  
        - 'CMDLINE Details'  
```

### Prepare the needed packages
Only need to execute once.
```bash
    $ cd svr_info_ek
    $ python3 server_info.py -p
```

### Start Testing
The tests include conformance test and PCIE topology info dump.
If there is no compared board result, the default is to compare the DUT itself.

```bash
    $ cd svr_info_ek
    $ python3 server_info.py
```
check "Result.xlsx" under `svr_info_ek` folder

Once it created `board_info.txt` under `svr_info_ek` folder, you can rename it as the future compared board result.
```bash
    $ mv board_info.txt golden_board_info.txt
```
Then use below command to generate the report.
```bash
    $ cd svr_info_ek
    $ python3 server_info.py -c golden_board_info.txt
```

You can also define the output report path.
```bash
    $ cd svr_info_ek
    $ python3 server_info.py -c golden_board_info.txt -o your_output_path
```

## How to scale for more tests
This section provides some guidline about how to add tests and parse data to report.
Briefly introduce the related files:

| File name | Description |
| :---        | :---        |
| svr_info_helper.sh | (From [svr_info](https://soco.intel.com/groups/svrinfo) project)The shell script to start various testing to DUT |
| svrinfo.py | (From [svr_info](https://soco.intel.com/groups/svrinfo) project)The python script to parse the info from the generated result |
| svr_info_helper_extend.sh | Extend from svr_info_helper.sh, to add more test |
| svrinfo_extend.py | Extend from svrinfo.py, to parse the information of newly added test |
| gen_result_svr.py | Incording to the parsed information, output the Excel report. |
| svr_info.yml | The file define the tests user wants to show at excel report |

Please keep origin files `svr_info_helper.sh` and `svrinfo.py` without updating, so that we can easily keep update with new features from [svr_info](https://soco.intel.com/groups/svrinfo) project.

Therefore, the effort is to update `svr_info_helper_extend.sh`, `svrinfo_extend.py`, `gen_result_svr.py`, and `svr_info.yml`.
Below takes some example of using these three files:
### [svr_info_helper_extend.sh]
If you want to add command to dump system cmdline info.
```bash
$ vim svr_info_helper_extend.sh

*Follow the format
printf "\n> your_command \n"
your_command

EX:
printf "\n> cat /proc/cmdline: \n"
cat /proc/cmdline
```
### [svrinfo_extend.py]
Add the function to parse specific information at the log file.
There are mainly two kinds of function to obtain data.
1. Obtain the specific result of test from log file, needs to define the regular expression rule
```bash
#Example for get some BIOS information from log of commands "lscpu", "cpuid -1", "dmesg".
#regular expression for parsing log
BIOSPAT = OrderedDict([
    ('Hyper-Threading Enabled', r'^Thread\(.*:\s*(.+?)\n'),
    ('Turbo Enabled', r'\s*Intel Turbo Boost Technology\s*= (.+?)\n'),
    ('Power & Perf Policy', None),
    ('Vt-d Enabled', r'(Directed\sI.O)'),
])

#Please add the parsing function under class Svrinfo.
class Svrinfo(Svrinfo):
    def get_bios_info_ek(self):
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
        return rethosts
```
2. obtain all result of test from log file 
```bash
#Example for get result from command `cmdline`.
class Svrinfo(Svrinfo):
    def get_cmdline(self):
        """Get MLC bandwidth"""
        rethosts = OrderedDict((k, []) for k in self._cmdict)
        for host, cmdout in self.__get_cmd_gen("cmdline"):
            rethosts[host] = cmdout

        return rethosts
```
### [gen_result_svr.py]
From the above return value `rethosts`, then write the data to Excel sheet.

If the expected Excel output format like below, there are two common functions can be followed, `gen_report_single_result()` and `gen_report()`

1. Example output for `gen_report_single_result()`
This output type will show all log result from specific testing command.  

```bash
gen_report_single_result('CMDLINE Details', 'CMDLINE Info', s.get_cmdline(), customer.get_cmdline())
```
| CMDLINE Info | dut | golden |
| :---        | :---        | :---        |
|  | BOOT_IMAGE=(loop)/boot/vmlinuz-4.15.0-99-generic findiso=/iso/nfviek-live.iso boot=live isolcpus=2-23,26-47,50-71,74-95 rcu_nocbs=2-23,26-47,50-71,74-95 nmi_watchdog=0 audit=0 nosoftlockup intel_pstate=disable processor.max_cstate=1 intel_idle.max_cstate=1 hpet=disable mce=off numa_balancing=disable default_hugepagesz=1GB hugepagesz=1G hugepages=12 iommu=pt intel_iommu=on | BOOT_IMAGE=(loop)/boot/vmlinuz-4.15.0-96-generic findiso=/iso/nfviek-live.iso boot=live isolcpus=2-23,26-47,50-71,74-95 rcu_nocbs=2-23,26-47,50-71,74-95 nmi_watchdog=0 audit=0 nosoftlockup intel_pstate=disable processor.max_cstate=1 intel_idle.max_cstate=1 hpet=disable mce=off numa_balancing=disable default_hugepagesz=1GB hugepagesz=1G hugepages=12 iommu=pt intel_iommu=on |



2. Example output for `gen_report()`
This output type will show specific log result from the regular expression
```bash
gen_report('BIOS Details', 'BIOS Info', s.get_bios_info_ek(), customer.get_bios_info_ek())
```
| BIOS Info | dut | golden |
| :---        | :---        | :---        |
| Hyper-Threading Enabled | Yes | Yes |
| Turbo Enabled | false | false |
| Power & Perf Policy | Performance | Performance |
| Vt-d Enabled | Yes | Yes |

If there are special format requriment, you can define by yourself.

Because `gen_result_svr.py` is associated with `svr_info.yml`, user should update the new test item as below format.
```bash
If user add the new test called 'CMDLINE Details'
$ vim gen_result_svr.py

for info in cfg['svr_info_list']:
    if info == 'Host Name and Time':
        gen_report('Host Name and Time', 'Host Info', s.get_sys(), customer.get_sys())
    elif info == 'System Details':
        gen_report('System Details', 'System Info', s.get_sysd(), customer.get_sysd())
    elif info == 'CPU Details':
        gen_report('CPU Details', 'CPU Info', s.get_cpu(), customer.get_cpu())
    elif info == 'Memory Details':
        gen_report('Memory Details', 'Memory Info', s.get_mem(), customer.get_mem())
    elif info == 'Memory Topology for hosts: dut.':
        gen_report_dimm('Memory Topology for hosts: dut.', s.get_dimms(), customer.get_dimms())
    elif info == 'Memory Bandwidth -vs- Latency Performance Chart :':
        gen_mem_text('Memory Performance')
        gen_report_graph('Memory Bandwidth -vs- Latency Performance Chart :', s.get_loadlat(), customer.get_loadlat())
    elif info == 'Network Details':
        gen_report_net('Network Details', 'Network Info', s.get_net(), customer.get_net())

    elif info == 'BIOS Details':
        gen_report('BIOS Details', 'BIOS Info', s.get_bios_info_ek(), customer.get_bios_info_ek())
    elif info == 'CMDLINE Details':
        gen_report_single_result('CMDLINE Details', 'CMDLINE Info', s.get_cmdline(), customer.get_cmdline())
```

### [svr_info.yml]
Once user update the test item, need to include it to the execution list.

```bash
$ vim svr_info.yml

*follow the format to add the defined test name

svr_info_list:
  - 'Host Name and Time'
  - 'System Details'
  - 'CPU Details'
  - 'BIOS Details'
  - 'Memory Details'
  - 'Memory Topology for hosts: dut.'
  - 'Memory Bandwidth -vs- Latency Performance Chart :'
  - 'Network Details'
  - 'CMDLINE Details'
```

## Option
### [Select testing] Server Conformance test
This test only provides the system conformance info.
```bash
    $ cd svr_info_ek
    $ ./svr_info_helper.sh | tee board_info.txt
    
    # the -i 'board_info.txt' can be updated to target compared system
    $ python3 gen_result_svr.py -c board_info.txt -i board_info.txt

```
check "Result.xlsx" under `svr_info_ek` folder


### [Select testing] PCIE Topology Dump
This test only provides the system PCIE topology info.
```bash
    $ cd svr_info_ek
    $ cd pcie
    $ bash run.sh | tee dump.txt
    $ python3 pcie_parsing.py
```
check "Result.xlsx" under `pcie` folder

## Legal

Intel&reg; disclaims all express and implied warranties, including without
limitation, the implied warranties of merchantability, fitness for a
particular purpose, and non-infringement, as well as any warranty arising
from course of performance, course of dealing, or usage in trade.

This document contains information on products, services and/or processes in
development.  All information provided here is subject to change without
notice. Contact your Intel&reg; representative to obtain the latest forecast
, schedule, specifications and roadmaps.

The products and services described may contain defects or errors known as
errata which may cause deviations from published specifications. Current
characterized errata are available on request.

Copies of documents which have an order number and are referenced in this
document may be obtained by calling 1-800-548-4725 or by visiting
www.intel.com/design/literature.htm.

Intel, the Intel logo are trademarks of Intel Corporation in the U.S.
and/or other countries.
