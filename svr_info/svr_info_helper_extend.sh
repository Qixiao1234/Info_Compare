#!/bin/bash
printf "\n> cat /proc/cmdline: \n"
cat /proc/cmdline
printf "\n> dmesg: \n"
dmesg
printf "\n> gcc --version: \n"
gcc --version

printf "> java -version: \n"
java -version

printf "> cpupower idle-info: \n"
cpupower idle-info

# echo "obase=2;$(rdmsr -f 2:0 0xE2)" | bc

printf "\n> msrinfo: "
printf "\nPKGC: "
echo "obase=2;$(rdmsr -f 2:0 0xE2)" | bc
printf "\nTurbo Enable: "
rdmsr -f 32:32 0x199
printf "\nEPB: "
rdmsr 0x1b0
printf "\nPC1E: "
rdmsr -f 1:1 0x1FC
printf "\nDynamic Switching: "
rdmsr -f 24:24 0x1FC
printf "\nEE Policy Control: "
rdmsr -f 23:23 0x1FC
printf "\nSystem Agent PM Control: "
rdmsr -f 22:22 0x1FC
printf "\nUncore Min Freq Limits: "
rdmsr -df 14:8 0x620
printf "\nUncore Max Freq Limits: "
rdmsr -df 6:0 0x620
printf "\nHWP Enable: "
rdmsr 0x770
printf "\nEPP: "
echo "obase=2;$(rdmsr -f 31:24 0x774)" | bc
printf "\nMax Frequency: "
rdmsr -df 15:8 0x774
printf "\nMin Frequency: "
rdmsr -df 7:0 0x774
printf "\nEnergy Efficient Turbo: "
rdmsr -f 19:19 0x1fc
printf "\nSMI_Count: "
rdmsr 0x34
printf "\nMSR_PPIN: "
rdmsr 0x4F
printf "\nIA32_BIOS_Sign_ID: "
rdmsr 0x8B
printf "\nPlatform_Info: "
rdmsr 0xCE
printf "\nMSR_PKG_CST_Config_Control: "
rdmsr 0xE2
printf "\nIA32_Perf_Status: "
rdmsr 0x198
printf "\nIA32_Perf_Ctl: "
rdmsr 0x199
printf "\nIA32_Therm_Status: "
rdmsr 0x19C
printf "\nIA32_MISC_Enable: "
rdmsr 0x1A0
printf "\nPrefetch_CTL: "
rdmsr 0x1A4
printf "\nIA32_Engergy_Perf_Bias: "
rdmsr 0x1B0
printf "\nIA32_Package_Therm_Status: "
rdmsr 0x1B1
printf "\nMSR_Power_CTL: "
rdmsr 0x1FC
printf "\nMSR_Core_C6_Residency: "
rdmsr 0x3FD
printf "\nUncore_Ratio_Limit: "
rdmsr 0x620
printf "\nUncore_Perf_status: "
rdmsr 0x621
printf "\nIA_Perf_Limit_Reason: "
rdmsr 0x64F
printf "\nIA32_HWP_Request: "
rdmsr 0x774

printf "\n> frequency_info: \n"
cpupower frequency-info

printf "> idle_info: \n"
cpupower idle-info

printf "> ptu or ptat data: \n"
echo y|ptu -mon -t 30
echo y|ptat -mon -t 30

######################################
printf "> glibc_info: \n"
rpm -qa | grep glibc

printf "> lsb_release -a: \n"
lsb_release -a

######################################
#

g_ret_data=0
g_ret_interface=0

#socket1 core id
#core1=0
core_id=0
#socker2 core id
#core2=`lscpu | grep "Core(s) per socket" | awk '{print $4}'`

#for core_id in {$core1,$core2}
#do

wait_until_run_busy_cleared(){
run_busy=1
while [[ $run_busy -ne 0 ]]
do 
  rd_interface=`rdmsr -p $core_id 0xb0`
  run_busy=$[rd_interface & 0x80000000]
  if [ $run_busy -eq 0 ]; then
    #not busy, just return
    break
  else
    echo "====warning:RUN_BUSY=1.sleep 1,then retry"
    sleep 1
  fi
done
}



#hwdrc_write(){
#input 1: the value of OS Mailbox Interface for write operation
#input 2: the value of OS Mailbox Data
#return OSmailbox interface status in g_ret_interface
#value_interface=$1
#value_data=$2
#wait_until_run_busy_cleared
#wrmsr -p $core_id 0xb1 $value_data
#the value_interface should include the RUN_BUSY,and all other fileds including COMMANDID,sub-COMMNADID,MCLOS ID(for attribute)
#wrmsr -p $core_id 0xb0 $value_interface
#wait_until_run_busy_cleared
#g_ret_interface=`rdmsr -p $core_id 0xb0`
#}



hwdrc_read(){
#input: the value of OS Mailbox Interface for read operation
#retrun hwdrc reg read value in $g_ret_data
#return OSmailbox interface status in $g_ret_interface
value_interface=$1
wait_until_run_busy_cleared
wrmsr -p $core_id 0xb0 $value_interface
wait_until_run_busy_cleared
g_ret_interface=`rdmsr -p $core_id 0xb0`
g_ret_data=`rdmsr -p $core_id 0xb1 --zero-pad`
g_ret_data=${g_ret_data:8:8}
}


#echo "check socket="$core_id

#read_value(){
#echo "Read_PM_Config"
hwdrc_read 0x80000694
#echo "0x80000694="$g_ret_data
printf "> 0x80000694 0xb1: $g_ret_data \n"
#echo "Write_PM_Config"
#hwdrc_read 0x80000695
#echo "0x80000695="$g_ret_data
}





if [ "$1" = "read" ]
then
	read_value
fi

if [ "$1" = "write" ]
then
	write_value $2
fi

#done

#usage:
#read cmd: ./mailbox.sh read
#write cmd: ./mailbox.sh write 0x0311(utilpoint+ufreq)


