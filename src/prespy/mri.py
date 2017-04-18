# coding: utf-8
from .logfile import load
from prespy.exceptions import DataNotFoundException
from collections import defaultdict

def mri_timing(logfile, pulsecode=199, events=[]):
    """Load the logfile and extract timing information for events in relation
    to the first pulsecode detected. Each event is either a string to match to
    a code, or a tuple with the column name and the column value to match"""
    logevts = load(logfile).events
    for evt in logevts:
        if evt.code == pulsecode:
            firstpulsetime = evt.time_sec
            break
    else:
        raise DataNotFoundException('Pulse code {} not found in file: {}'.format(pulsecode, logfile))

    tupleevts = [e for e in events if isinstance(e, tuple)]
    categories = defaultdict(list)
    for evt in logevts:
        if evt.code == pulsecode:
            categories['pulses'].append(evt.time_sec - firstpulsetime)
        elif evt.code in events:
            categories[evt.code].append(evt.time_sec - firstpulsetime)
        for te in tupleevts:
            if evt.data[te[0]] == te[1]:
                categories[te[1]].append(evt.time_sec - firstpulsetime)
    return categories
        
        
def write_matlab(mfile, timing_data):
    """write the timing data to a matlab .m file format"""
    with open(mfile, 'w') as writer:
        2
        writer.write(

    
    
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
        #print('{} = [ {} ]'.format('a', ' '.join(['{:.2f}'.format(da/100.0) for da in d['a']])))
        print(a, np.array(categories[a]))
        bf.write(a + ' = ' + str(np.around(np.array(categories[a]) / 10000.0, 2)) + '\n')
