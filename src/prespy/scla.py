# coding: utf-8
from __future__ import division
import statistics as stat
from prespy.logfile import load
from copy import deepcopy
import wave
import struct

datasets = {'Port_to_Port': None, 'Snd_to_Snd': None, 'Port_Length': None, 'Snd_Upper_Bound': [], 'Snd_Lower_Bound': []}


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
        super().__init__()
        self.udat = udat


class SoundError(Exception):
    """raised when there is an issue loading the soundfile"""
    def __init__(self, msg):
        super().__init__()
        self.msg = msg


def stdStats(datasets):
    """Run the full gamut of standard stats on each dataset"""
    stats = {}
    for d in datasets:
        stats[d] = {}
        data = datasets[d]
        stats[d]['mean'] = stat.mean(data)
        stats[d]['min'] = min(data)
        stats[d]['max'] = max(data)
        stats[d]['stddev'] = stat.stdev(data)
        stats[d]['rawdata'] = data
    return stats


def extract_channel_events(channel, maxdur=0.012, thresh=0.2, samplerate=44100):
    '''From a single channel, extract events that reach *thresh*old and last
    for *maxdur*'''
    events = []
    lastevt = -20000
    for index, value in enumerate(channel):
        if index - lastevt > maxdur * samplerate:
            if abs(value) > thresh:
                events.append(index / samplerate)
                lastevt = index
    return events


def extract_sound_events(soundfile, schannel=1, maxdur=0.012, thresh=0.2, plot=False, runid='scla'):
    fs, sdata = wavLoad(soundfile)  # wavfile.read(soundfile)
    # Grab channels
    port = sdata[1 - schannel]
    snd = sdata[schannel]
    # Normalise channels
    maxp = max(port)
    maxs = max(snd)
    port = [p / maxp for p in port]
    snd = [s / maxs for s in snd]
    port_events = extract_channel_events(port, maxdur=maxdur, thresh=thresh, samplerate=fs)
    snd_events = extract_channel_events(snd, maxdur=maxdur, thresh=thresh, samplerate=fs)
    if plot:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print('matplotlib not found, skipping plot of first sound')
        plt.plot(snd[int(snd_events[0] * fs) - 100:int((snd_events[0] + maxdur) * fs)])
        plt.savefig(runid + '_firstsnd.png')
        plt.close()
    return fs, port_events, snd_events, port


def scla(soundfile=None, logfile=None, **kwargs):
    """Implements similar logic to Neurobehavioural Systems SCLA program"""
    log = load(logfile)

    fs, pcodes, snds, port = extract_sound_events(soundfile, **kwargs)
    if (len(log.events) != len(pcodes)) or (len(pcodes) != len(snds)):
        raise ExtractError(log.events, pcodes, snds)

    thisdata = deepcopy(datasets)
    for evt in range(len(snds)):
        # Uncertainty in seconds
        uncertainty = float(log.events[evt].data['Uncertainty (Time)']) * 0.0001
        thisdata['Snd_Lower_Bound'].append(snds[evt] - pcodes[evt])
        thisdata['Snd_Upper_Bound'].append(snds[evt] - pcodes[evt] + uncertainty)
    td, pl = timing(port, pcodes, snds, fs, **kwargs)
    thisdata['Port_to_Port'] = td['pcodes']
    thisdata['Snd_to_Snd'] = td['snds']
    thisdata['Port_Length'] = pl
    return stdStats(thisdata)


def timing(port, pcodes, snds, fs, maxdur=0, thresh=0, **kwargs):
    """extract extra info about port duration and time between stimuli"""
    timediffs = {'pcodes': [], 'snds': []}
    portlengths = []
    for p in range(1, len(pcodes)):
        timediffs['pcodes'].append(pcodes[p] - pcodes[p - 1])
    for s in range(1, len(snds)):
        timediffs['snds'].append(snds[s] - snds[s - 1])
    for p in pcodes:
        span = range(int(p * fs) + 1, int((p + maxdur * 1000) * fs))
        for pt in span:
            if port[pt] < thresh:
                portlengths.append(pt / fs - p)
                break
    return timediffs, portlengths


def wavLoad(fname):
    '''Load a 2 channel wavefile into a list of two element lists
    Taken from: http://stackoverflow.com/a/2602334/1468125'''
    wav = wave.open(fname, "r")
    (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams()
    frames = wav.readframes(nframes * nchannels)
    out = struct.unpack_from("%dh" % nframes * nchannels, frames)

    if nchannels == 2:
        return framerate, (out[0::2], out[1::2])  # ((L, R) channels)
    else:
        raise SoundError('Should be two and only two channels in recorded sound')
