# coding: utf-8
from __future__ import division
import statistics as stat
from .logfile import load
from .exceptions import ExtractError, SoundError
from copy import deepcopy
import wave
import struct
import warnings
import logging

datasets = {'Port_to_Port': None, 'Snd_to_Snd': None, 'Port_Length': None, 'Snd_Upper_Bound': [], 'Snd_Lower_Bound': []}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s: %(message)s'))
logger.addHandler(ch)


def stdStats(datasets):
    """Run the full gamut of standard stats on each dataset"""
    stats = {}
    for d in datasets:
        logger.info('Calculating stats for %s', d)
        stats[d] = {}
        data = datasets[d]
        stats[d]['mean'] = stat.mean(data)
        stats[d]['min'] = min(data)
        stats[d]['max'] = max(data)
        stats[d]['stddev'] = stat.stdev(data)
        stats[d]['rawdata'] = data
    return stats


def _exceeds_threshold(value, threshold):
    """If the threshold is negative, determine if value is more negative
    if the threshold is positive, determine is the value is more positive"""
    if threshold < 0:
        return value < threshold
    return value > threshold


def extract_channel_events(channel, maxdur=0.012, thresh=0.2, samplerate=44100):
    '''From a single channel, extract events that reach *thresh*old and last
    for *maxdur*'''
    events = []
    lastevt = -20000
    for index, value in enumerate(channel):
        if index - lastevt > maxdur * samplerate:
            if _exceeds_threshold(value, thresh):
                events.append(index / samplerate)
                lastevt = index
    return events


def _fix_for_sigchange(kwargs):
    '''Populate with channel specific key,vals when called with non specific versions'''
    if 'maxdur' in kwargs:
        if 'snddur' in kwargs or 'portdur' in kwargs:
            raise RuntimeError('maxdur argument in arguments AND either snddur or portdur in arguments')
        kwargs['snddur'] = kwargs['maxdur']
        kwargs['portdur'] = kwargs['maxdur']
        logger.warning('modifying keyword arguments: %s', kwargs)
        warnings.warn('maxdur argument is deprecated and will be removed in a future release', DeprecationWarning)
    if 'thresh' in kwargs:
        if 'sndthresh' in kwargs or 'portthresh' in kwargs:
            raise RuntimeError('thresh argument in arguments AND either sndthresh or portthresh in arguments')
        kwargs['sndthresh'] = kwargs['thresh']
        kwargs['portthresh'] = kwargs['thresh']
        logger.warning('modifying keyword arguments: %s', kwargs)
        warnings.warn('thresh argument is deprecated and will be removed in a future release', DeprecationWarning)
    return kwargs


def extract_sound_events(soundfile, schannel=1, plot=False, runid='scla', **kwargs):
    fs, sdata = wavLoad(soundfile)  # wavfile.read(soundfile)
    # Grab channels
    port = sdata[1 - schannel]
    snd = sdata[schannel]
    # Normalise channels
    maxp = max(port)
    maxs = max(snd)
    port = [p / maxp for p in port]
    snd = [s / maxs for s in snd]
    port_events = extract_channel_events(port,
                                         maxdur=kwargs['portdur'],
                                         thresh=kwargs['portthresh'],
                                         samplerate=fs)
    snd_events = extract_channel_events(snd,
                                        maxdur=kwargs['snddur'],
                                        thresh=kwargs['sndthresh'],
                                        samplerate=fs)
    if plot:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning('matplotlib not found, skipping plot of first sound')
        plt.plot(snd[int(snd_events[0] * fs) - 100:int((snd_events[0] + kwargs['snddur']) * fs)])
        plt.savefig(runid + '_firstsnd.png')
        plt.close()
    return fs, port_events, snd_events, port


def scla(soundfile=None, logfile=None, **kwargs):
    """Implements similar logic to Neurobehavioural Systems SCLA program"""
    log = load(logfile)
    # Fix for previous call signatures still in use
    kwargs = _fix_for_sigchange(kwargs)

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


def timing(port, pcodes, snds, fs, portdur=0, portthresh=0, **kwargs):
    """extract extra info about port duration and time between stimuli"""
    timediffs = {'pcodes': [], 'snds': []}
    portlengths = []
    # Port evt to Port evt in time
    for p in range(1, len(pcodes)):
        timediffs['pcodes'].append(pcodes[p] - pcodes[p - 1])
    # Sound evt to Sound evt in time
    for s in range(1, len(snds)):
        timediffs['snds'].append(snds[s] - snds[s - 1])
    # Length of each port event
    for p in pcodes:
        span = range(int(p * fs) + 1, int((p + portdur * 1000) * fs))
        for pt in span:
            if not _exceeds_threshold(port[pt], portthresh):
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
