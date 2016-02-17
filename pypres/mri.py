# coding: utf-8
import numpy as np
with open('pilot01-FoodAddiction3.log', 'r') as lf:
    lines = lf.read().splitlines()
    
header = lines[3].split('\t')
data = [l.split('\t') for l in lines[5:]]
codecol = header.index('Code')
timecol = header.index('Time')
catcol = header.index('Category(str)')
for t in data:
    if t[codecol] == '199':
        firstpulse = int(t[timecol])
        break
    
categories = {}
categories['fixations'] = []
categories['gaps'] = []
categories['pulses'] = []
inblock = False
for e in data:
    e[timecol] = int(e[timecol])

for t in data:
    if t[codecol] == '199':
        categories['pulses'].append(t[timecol] - firstpulse)
    elif t[codecol] == 'fix':
        categories['fixations'].append(t[timecol] - firstpulse)
        inblock = False
    elif t[codecol] == 'gap':
        categories['gaps'].append(t[timecol] - firstpulse)
        inblock = False
    elif t[catcol]:
        if not inblock:
            if t[catcol] in categories:
                categories[t[catcol]].append(t[timecol] - firstpulse)
            else:
                categories[t[catcol]] = [t[timecol] - firstpulse]
            inblock = True

np.set_printoptions(precision=2, suppress=True, linewidth=20000)
with open('blocks.m', 'w') as bf:
    for a in categories:
        print(a, np.array(categories[a]))
        bf.write(a + ' = ' + str(np.around(np.array(categories[a])/10000.0, 2)) + '\n')
