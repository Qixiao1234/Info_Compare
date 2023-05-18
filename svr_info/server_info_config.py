import subprocess
import os
import sys

report_path = "/root/work/Intel_NFVI_EK/output"

file_dir = os.path.dirname(sys.argv[0])  # path of this code

if file_dir != '.' and file_dir != '':
    os.chdir(file_dir)

def get_num_socket():
    cmd = "lscpu"
    output=subprocess.check_output(cmd, shell=True).decode().strip()
    output = output.split('\n')
    for line in output:
        if "Socket(s):" in line:
            for str in line.split():
                if str.isdigit():
                    return int(str)

def get_soc_cpu_model():
    cmd = "lscpu"
    output=subprocess.check_output(cmd, shell=True).decode().strip()
    output = output.split('\n')
    for line in output:
        if "Model name:" in line:
            for str in line.split():
                if "Atom" in str:
                    return "dnv"
                elif "Xeon" in str:
                    return "skl_d"
            #default CPU as Denverton
            return "dnv"

def main():

    num_socket = get_num_socket()
    if num_socket == 1:
        cpu_model = get_soc_cpu_model()
        if cpu_model == "dnv":
            sample_file = "dnv_c3958.txt"
        elif cpu_model == "skl_d":
            sample_file = "skl_d2187.txt"
        else:
            sample_file = "skl_d2187.txt"
        sample_file_path = "/root/work/Intel_NFVI_EK/output/%s" %(sample_file)
    else:
        sample_file_path = "/root/work/Intel_NFVI_EK/output/gold_sp_6252.txt"

    # Detect Binary, Python
    if os.path.isfile("server_info"):
        cmd = "./server_info -c {0} -o {1}".format(sample_file_path, report_path)
    else:
        cmd = "python server_info.py -c {0} -o {1}".format(sample_file_path, report_path)

    os.system(cmd)
    print (cmd)
 
    # Remove redundant file
    fio_path = "/dev/shm/fio_test_file"
    if os.path.isfile(fio_path):
        os.remove(fio_path)


if __name__ == "__main__":
    main()