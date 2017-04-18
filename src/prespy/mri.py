# coding: utf-8
from .logfile import load
from prespy.exceptions import DataNotFoundError
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
        raise DataNotFoundError('Pulse code {} not found in file: {}'.format(pulsecode, logfile))

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


def write_matlab(mfile, timing_data, dec_places=2):
    """write the timing data to a matlab .m file format"""
    with open(mfile, 'w') as writer:
        for category in timing_data:
            formatted = ' '.join(['{0:.{1}f}'.format(secs, dec_places) for secs in timing_data[category]])
            writer.write('{} = [ {} ]\n'.format(category, formatted))
