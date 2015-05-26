# coding: utf-8
import numpy as np
with open('scott-PTDS_Emotion2.log', 'r') as lf:
    lines = lf.read().splitlines()
    
header = lines[3].split('\t')
data = [l.split('\t') for l in lines[5:]]
codecol = header.index('Code')
timecol = header.index('Time')
for t in data:
    if t[codecol] == '199':
        firstpulse = int(t[timecol])
        break
    
pulses = []
fearblocks = []
happyblocks = []
neutralblocks = []
fixations = []
inblock = 0
for e in data:
    e[timecol] = int(e[timecol])

for t in data:
    if t[codecol] == '199':
        pulses.append(t[timecol] - firstpulse)
    elif t[codecol] == 'FIX':
        fixations.append(t[timecol] - firstpulse)
        inblock = 0
    elif t[codecol].startswith('Fear'):
        if inblock == 0:
            fearblocks.append(t[timecol] - firstpulse)
        inblock += 1
    elif t[codecol].startswith('Happy'):
        if inblock == 0:
            happyblocks.append(t[timecol] - firstpulse)
        inblock += 1
    elif t[codecol].startswith('Neutral'):
        if inblock == 0:
            neutralblocks.append(t[timecol] - firstpulse)
        inblock += 1

all = {'pulses':pulses, 'fixations':fixations, 'happy':happyblocks, 'fear':fearblocks, 'neutral':neutralblocks}
np.set_printoptions(linewidth=20000)
with open('blocks.m', 'w') as bf:
    for a in all:
        bf.write(a + ' = ' + str(np.array(all[a])/10000.0) + '\n')
