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

    def __str__(self):
        """Represent this error as a string"""
        elements = [self.message, len(self.logData), len(self.portData), len(self.sndData)]
        return '{}\nLengths: Log({}), Port({}), Snds({})'.format(*elements)


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


def extract_channel_events(channel, maxdur=0.012, thresh=0.2, samplerate=44100):
    '''From a single channel, extract events that reach *thresh*old and last
    for *maxdur*'''
    events = []
    lastevt = -20000
    for index, value in enumerate(channel):
        if index - lastevt > maxdur*samplerate:
            if abs(value) > thresh:
                events.append(index/samplerate)
                lastevt = index
    return events


def extract_sound_events(soundfile, schannel=1, maxdur=0.012, thresh=0.2, plot=True, runid='scla'):
    fs, sdata = wavfile.read(soundfile)
    # Grab channels
    port = sdata.T[1-schannel]
    snd = sdata.T[schannel]
    # Normalise channels
    port = port/max(port)
    snd = snd/max(snd)
    port_events = extract_channel_events(port, maxdur=maxdur, thresh=thresh, samplerate=fs)
    snd_events = extract_channel_events(snd, maxdur=maxdur, thresh=thresh, samplerate=fs)
    if plot:
        plt.plot(snd[int(snd_events[0]*fs)-100:int((snd_events[0]+maxdur)*fs)])
        plt.savefig(runid+'_firstsnd.png')
        plt.close()
    return fs, port_events, snd_events, port


def scla(soundfile=None, logfile=None, **kwargs):
    """Implements similar logic to Neurobehavioural Systems SCLA program"""
    log = load(logfile)

    fs, pcodes, snds, port = extract_sound_events(soundfile, **kwargs)
    if (len(log.events) != len(pcodes)) or (len(pcodes) != len(snds)):
        raise ExtractError(log.events, pcodes, snds)

    datasets = {}
    datasets['Lower Bound'] = []
    datasets['Upper Bound'] = []
    for evt in range(len(snds)):
        datasets['Lower Bound'].append(snds[evt] - pcodes[evt])
        datasets['Upper Bound'].append(snds[evt] - pcodes[evt] +
                                       float(log.events[evt].data['Uncertainty (Time)'])*0.0001)  # Uncertainty in seconds
    td, pl = timing(port, pcodes, snds, fs, **kwargs)
    datasets['Port Time Diffs'] = td['pcodes']
    datasets['Snd Time Diffs'] = td['snds']
    datasets['Port Code Lengths'] = pl
#    import pdb; pdb.set_trace()
    return stdStats(datasets)


def timing(port, pcodes, snds, fs, maxdur=0, thresh=0, **kwargs):
    """extract extra info about port duration and time between stimuli"""
    timediffs = {'pcodes': [], 'snds': []}
    portlengths = []
    for p in range(1, len(pcodes)):
        timediffs['pcodes'].append(pcodes[p] - pcodes[p-1])
    for s in range(1, len(snds)):
        timediffs['snds'].append(snds[s] - snds[s-1])
    for p in pcodes:
        span = range(int(p*fs) + 1, int((p+maxdur*1000)*fs))
        for pt in span:
            if port[pt] < thresh:
                portlengths.append(pt/fs - p)
                break
    return timediffs, portlengths
