#! /bin/bash
echo "please input the cmd"

for line in `cat yum_list.txt`
do	
	echo $line
	yum --help
	if [ $? -ne 0 ]; then
	#if [ -n "uname -a|grep -i debian" ]; then
		apt-get -y install $line
		pkill -9 apt-get
	else
		yum -y install $line
		pkill -9 yum
	fi
	
done

IFS=$'\n'	
#for line in `cat cmd_list.txt `
#do		

freq_drv_pol() {
    echo "CPU Freq Driver: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver 2>/dev/null)"
    echo "CPU Freq Governor: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)"
}

turbo_test() {
    tcmd="turbostat -i 2"
    (sh -c "$tcmd 2>/dev/null &";stress-ng --cpu 1 -t 9s 2>&1;stress-ng --cpu 0 -t 5s --metrics-brief 2>&1;kill `ps -e|grep turbostat|awk '{print $1}'`)|awk '$0~"stress" {print $0} $1=="Package" || $1=="CPU" || $1=="Core" {if(f!=1) print $0;f=1} $1=="-" {print $0}'
}

#		echo $line
#        eval $line
#        if [ $? -eq 0 ]        
#        then  
#            echo $line >> success.txt
#		else
#			echo $line >> error.txt
#        fi
#done