# encoding= utf-8
import subprocess
import os
import sys
import time

sys.path.append("pcie")
import pcie_parsing
import gen_result_svr
import string
import io

from argparse import ArgumentParser

with open('loadnum.txt', 'r+', encoding='utf-8') as a:
    run_num = a.readlines()[-1]
    # print(int(run_num.strip()))
    a.write(str(int(run_num.strip()) + 1) + '\n')

work_dir = os.getcwd()
board_info_path = work_dir + "/data/" + str(run_num).strip() + "_board_info.txt"
compare_board_info_path = board_info_path
# print('board_info_path:' + board_info_path)

path_ramdisk = "/dev/shm/"
work_dir = os.getcwd()

report_path = work_dir + "/data"
pcie_tool_path = "pcie"


# 新增下载特定版本openpyxl
def pip3_openpyxl():
    cmd = 'pip3 install openpyxl==3.0.3'
    os.system(cmd)


# 编译
def compile_msrtool():
    print("compiling msrtool")
    my_env = dict(os.environ)
    my_cwd = '/dev/shm/msr-tools-master'
    cmd = "make 2>&1"
    sp = subprocess.Popen(cmd, env=my_env, cwd=my_cwd, shell=True, stderr=subprocess.STDOUT)
    if sp.wait() != 0:
        return False

    os.system("cp /dev/shm/msr-tools-master/rdmsr /usr/bin")
    os.system("cp /dev/shm/msr-tools-master/wrmsr /usr/bin")

    return True


def setup_locale():
    os.environ["LANGUAGE"] = "en_US.UTF-8"
    os.environ["LANG"] = "en_US.UTF-8"

    # This is for prevent error when writing board_info.txt, it will contain some strange unicode character
    os.environ["LC_ALL"] = "ANSI_X3.4-1968"

    os_name = get_os_name()
    if "ubuntu" in os_name.lower():
        print("Ubuntu: locale")
        os.system("localedef -i en_US -f UTF-8 en_US.UTF-8")
        os.system("update-locale LANG=en_US.UTF-8")
    elif "centos" in os_name.lower():
        print("CentOS: locale")
        os.system("localectl set-locale LANGUAGE=en_US.UTF-8")
        os.system("localectl set-locale LANG=en_US.UTF-8")


# 修改了下载地址，可能需要权限
def prepare_msrtool():
    if os.path.exists("msr-tools-1.3.zip") == False:
        print("download msrtool from internet")

        os.system(
            "git clone https://github.com/intel-innersource/applications.validation.mss-pmss-apps.linux-apps.msrtools.git")
    os.system("unzip -o msr-tools-1.3.zip -d /dev/shm")

    print("msrtool done")


def get_os_name():
    result = ""

    output = subprocess.getoutput('hostnamectl').strip()
    output = output.split('\n')
    for line in output:
        if "Operating System" in line:
            result = line.replace("  Operating System: ", "")

    return result


def prepare_mlc():
    os.system("cp mlc_v3.9a.tgz " + path_ramdisk)
    os.chdir(path_ramdisk)
    os.system("mkdir -p mlc")
    os.system("tar zxvf mlc_v3.9a.tgz -C mlc/")
    os.system("cp -rf mlc/Linux/mlc* /usr/bin")


# 修改了下载地址，可能需要权限
def checking_installed_ipmitool():
    cmd = "ipmitool"
    if os.path.exists("ipmitool") == False:
        os.system("git clone https://github.com/ipmitool/ipmitool.git")
    os.chdir(path_ramdisk)
    if os.path.exists("ipmitool") == False:
        os.system("cp -r ipmitool " + path_ramdisk)
    # os.system("tar zxvf ipmitool.tar.gz")

    os.chdir("ipmitool")
    # os.system("./configure")
    # os.system("make")
    # os.system("make install")


def install_cmd():
    os.system("./install_cmd.sh")


def prepare():
    install_cmd()
    prepare_msrtool()
    compile_msrtool()

    prepare_mlc()

    # checking_installed_ipmitool()


def main():
    global board_info_path, compare_board_info_path, report_path

    board_info_count = 0

    parser = ArgumentParser(description='svr_info_ek')
    parser.add_argument('-p', '--prepare', action='store_true',
                        help='To prepare the needed packages, recommand to execute first', default=False)
    parser.add_argument('-i', '--input', help='Input board_info.txt')
    parser.add_argument('-c', '--compare', help='Input another board_info.txt for comparison')
    parser.add_argument('-o', '--output', help='Enter the output excel report path')
    # parser.add_argument('-f','--full', help='Run all test')

    args = vars(parser.parse_args())

    if args['prepare'] == True:
        prepare()
        sys.exit(0)
    if args['input'] != None:
        if os.path.exists(args['input']):
            board_info_path = args['input']
            board_info_count = board_info_count + 1
    if args['compare'] != None:
        if os.path.exists(args['compare']):
            compare_board_info_path = args['compare']
            board_info_count = board_info_count + 1
    if args['output'] != None:
        if os.path.exists(args['output']):
            report_path = args['output']
            if not report_path.endswith('/'):
                report_path = report_path + '/'

            board_info_path = report_path + board_info_path
            if compare_board_info_path == board_info_path:
                compare_board_info_path = board_info_path

    if board_info_count == 2:
        dump_report()
    else:
        collect_info()
        dump_report()


def collect_info():
    setup_locale()

    os.system('clear')
    print("\n\n***********************************************************************")
    print('Analysing and generating Conformance report')
    print("***********************************************************************\n\n")

    os.chdir(work_dir)

    # =========================Start SVR info testing
    # incase permmision deny

    # svr_info_helper
    if os.path.isfile("svr_info_helper"):
        file_name = "svr_info_helper"
    else:
        file_name = "svr_info_helper.sh"

    os.system('chmod +x %s' % file_name)
    cmd = "./{0} -c all -n dut -t 30 -f /dev/shm/ | tee {1}".format(file_name, board_info_path)
    os.system(cmd)

    # svr_info_helper_extend
    if os.path.isfile("svr_info_helper_extend"):
        file_name = "svr_info_helper_extend"
    else:
        file_name = "svr_info_helper_extend.sh"
    os.system('chmod +x %s' % file_name)
    cmd = "./{0} | tee -a {1}".format(file_name, board_info_path)
    os.system(cmd)

    # =========================Start PCIE topology parsing
    os.chdir(pcie_tool_path)
    if os.path.isfile("run"):
        file_name = "run"
    else:
        file_name = "run.sh"
    os.system('chmod +x %s' % file_name)
    cmd = "./%s | tee dump.txt" % file_name
    os.system(cmd)

    # change locale setting back
    os.environ["LC_ALL"] = "en_US.UTF-8"

    os.chdir(work_dir)
    os.system('python3 collect_info_helper.py %s' % (board_info_path))


def dump_report():
    os.chdir(work_dir)

    # ===================Start parsing SVR info data and write to Excel
    if os.path.isfile(board_info_path):
        # Due to the dimm info from dmidecode is different between Purley and Whitely, update the board_info if the dut is Whitely based system
        output = open(board_info_path, 'r')

        with open(board_info_path, 'r') as f:
            output = f.readlines()
            print(output)
            adjust_need = False
            for line in output:
                if 'CPU0_' in line:
                    adjust_need = True

            if adjust_need:
                os.system("sed -i 's/CPU1_/CPU2_/' " + board_info_path)
                os.system("sed -i 's/CPU0_/CPU1_/' " + board_info_path)
            # currently to compare DUT vs DUT, can modify the second one by yourself
            gen_result_svr.main_binary(board_info_path, compare_board_info_path, report_path + '/')

            print("\n\n***********************************************************************")
            print("Conformance report is done!")
            print("***********************************************************************\n\n")
    else:
        print("Something wrong while running svr_info! board_info.txt does not exist!")

    # ===================Start parsing PCIE topology data and write to Excel
    pcie_data = pcie_tool_path + '/dump.txt'
    if os.path.isfile(pcie_data):

        os.chdir(pcie_tool_path)

        try:
            if os.path.isfile(report_path + '/' + str(run_num).strip() + '_Reports.xlsx'):
                pcie_parsing.main_binary(report_path + '/' + str(run_num).strip() + '_Reports.xlsx')
            else:
                pcie_parsing.main()
                print(
                    "Something wrong while running svr_info! you can only check PCIE topology info under folder 'pcie'")
        except Exception as err:
            print("[Error]: " + str(err))
            print("PCIE topology report is fail!")

        print("\n\n***********************************************************************")
        print("PCIE topology report is done!")
        print("***********************************************************************\n\n")
    else:
        print(
            "Something wrong while parsing pcie topology! dump.txt does not exist, maybe this system not support such commands")


if __name__ == "__main__":
    main()
