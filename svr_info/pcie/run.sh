#!/bin/bash
printf "\n> lspci -t: \n"
lspci -t
printf "\n> lspci | grep 'PCI bridge' | grep -v 'Root': \n"
lspci | grep 'PCI bridge' | grep -v 'Root'
printf "\n> lspci | grep Root: \n"
lspci | grep Root
printf "\n> dmesg | grep 'NUMA node': \n"
dmesg | grep 'NUMA node'
printf "\n\n"
