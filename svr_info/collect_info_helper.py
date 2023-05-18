import os
import sys

cmd = 'lspci -s 7f:1e.2 -xxx -x | grep e0 > temp.txt'
os.system(cmd)
with open('temp.txt', 'r', encoding='utf-8') as te:
    t = te.readline()
    print('=================================================================================================')
os.remove('temp.txt')

print(t)
n = t[16:27]
n = n.replace(' ', '')
n = int(n, 16)
n = '{:08b}'.format(n)

s = '\n' + '> PERF PLIMIT INFO:' + '\n' + 'PERF PLIMIT ENABLE: ' + n[31] + '\n' + 'PERF PLIMIT THRESHOLD: ' + str(int(n[26:31], 2)) + '\n' + 'PERF PLIMIT CLIP: ' + str(int(n[20:25], 2)) + '\n' + 'PERF PLIMIT DIFFERENTIAL: ' + str(int(n[17:20], 2)) + '\n'
# print(s)

with open(sys.argv[1], 'a', encoding='utf-8') as f:
    f.writelines(s)
