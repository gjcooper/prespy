# coding: utf-8
from __future__ import division
from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
from ..logfile import load


class ExtractError(Exception):
    """Raised when an extraction goes wrong"""
    def __init__(self, logData, portData, sndData):
        super(ExtractError, self).__init__()
        self.logData, self.portData, self.sndData = logData, portData, sndData
        self.message = 'Extraction error, detected code lengths do not match'


class ConvertError(Exception):
    """Raised when a log file number was not converted successfully"""
    def __init__(self, udat):
        super(ConvertError, self).__init__()
        self.udat = udat


def stdStats(datasets):
    """Run the full gamut of standard stats on each dataset"""
    stats = {}
    for d in datasets:
        stats[d] = {}
        data = datasets[d]
        stats[d]['mean'] = np.mean(data)
        stats[d]['min'] = min(data)
        stats[d]['max'] = max(data)
        stats[d]['stddev'] = np.std(data)
        stats[d]['rawdata'] = data
    return stats


def scla(pid, sfile, lfile, schan=1, mdur=0.012, thresh=0.2):
    """Implements similar logic to Neurobehavioural Systems SCLA program"""
    log = load(lfile)
    fs, sdata = wavfile.read(sfile)
    port = sdata.T[1-schan]
    snd = sdata.T[schan]
    mp = max(port)
    ms = max(snd)
    port = port/mp
    snd = snd/ms
    # Grab each port event into a list
    pcodes = []
    lcd = -20000  # Sufficiently small number
    for pi in range(len(port)):
        if pi - lcd > mdur*fs:
            if port[pi] > thresh:
                pcodes.append(pi/fs*1000)
                lcd = pi
    # Grab each snd event into a list
    snds = []
    lsd = -20000
    for si in range(len(snd)):
        if si - lsd > mdur*fs:
            if snd[si] > thresh:
                snds.append(si/fs*1000)
                lsd = si

    if (len(log.events) != len(pcodes)) or (len(pcodes) != len(snds)):
        raise ExtractError(log.events, pcodes, snds)

    datasets = {}
    datasets['Lower Bound'] = []
    datasets['Upper Bound'] = []
    unc = log.header['Uncertainty (Time)']
    for evt in range(len(snds)):
        datasets['Lower Bound'].append(snds[evt] - pcodes[evt])
        datasets['Upper Bound'].append(snds[evt] - pcodes[evt] +
                                       float(log.events[evt].data[unc])/10)
    td, pl = timing(port, pcodes, snds, fs, mdur, thresh)
    datasets['Port Time Diffs'] = td['pcodes']
    datasets['Snd Time Diffs'] = td['snds']
    datasets['Port Code Lengths'] = pl
#    import pdb; pdb.set_trace()
    plt.plot(snd[int(snds[0]*fs/1000)-100:int((snds[0]+mdur*1000)*fs/1000)])
    plt.savefig(pid+'_firstsnd.png')
    plt.close()
    return stdStats(datasets)


def timing(port, pcodes, snds, fs, mdur, thresh):
    """extract extra info about port duration and time between stimuli"""
    timediffs = {'pcodes': [], 'snds': []}
    portlengths = []
    for p in range(1, len(pcodes)):
        timediffs['pcodes'].append(pcodes[p] - pcodes[p-1])
    for s in range(1, len(snds)):
        timediffs['snds'].append(snds[s] - snds[s-1])
    for p in pcodes:
        span = range(int(p*fs/1000) + 1, int((p+mdur*1000)*fs/1000))
        for pt in span:
            if port[pt] < thresh:
                portlengths.append(pt/fs*1000 - p)
                break
    return timediffs, portlengths
