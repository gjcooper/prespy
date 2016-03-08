from __future__ import division
from .exceptions import LoadError
from datetime import datetime
from itertools import takewhile
import os


class Experiment:
    def __init__(self, name):
        self.name = name


class Measure:
    '''An object that represents some manipulation or subset of the data in
    question'''
    def __init__(self, name):
        self.name = name

    def build(self):
        """Should be set by user code, build a subset of a data object
        and return it"""
        raise NotImplementedError('Build should be defined by user code')


class Event:
    def __init__(self, bline, header):
        """Create Event info from line and header dict"""
        self.data = {h: (bline[header[h]] if header[h] < len(bline) else '')
                     for h in header}
        self.etype = self.data['Event Type']
        self.code = self.data['Code']
        self.time = float(self.data['Time'])/10  # In ms

    def __str__(self):
        return self.etype+':'+self.code+':'+str(self.time)

    def __repr__(self):
        return str(self)


class Record:
    def __init__(self, filename):
        if os.path.isfile(filename):
            self.source = os.path.abspath(filename)
            self._extract()
        else:
            raise LoadError('Err: Logfile not found', filename)

    def _extract(self):
        """Extract usable data from the file into the record dictionary
        """
        with open(self.source, 'r') as lf:
            lines = lf.read().splitlines()
        l = 0  # A pointer which we'll use to step through the file
        # Grab Scenario name
        if lines[l].split('-')[0].strip() == 'Scenario':
            self.exp = Experiment(lines[l].split('-')[1].strip())
            l += 1
        else:
            raise LoadError('Err: first line does not start with Scenario')
        # Get Logfile timestamp
        if lines[l].split('-')[0].strip() == 'Logfile written':
            self.timestamp = datetime.strptime(lines[l].split('-')[1].strip(),
                                               '%m/%d/%Y %H:%M:%S')
            l += 1
        else:
            raise LoadError('Err: second line does not contain timestamp')
        # Grab Logfile Header
        for line in lines[l:]:
            if line.startswith('Subject'):
                hline = line.split('\t')
                unc_types = [' (Duration)', ' (Time)']
                hline = [h + unc_types.pop() if h == 'Uncertainty' else h
                         for h in hline]
                self.header = {hline[c]: c for c in range(len(hline))}
                l += 1
                break
            else:
                l += 1
        if lines[l] != '':
            raise LoadError('Err: Expected blank line between header and body')
        # Grab data
        l += 1
        self.events = []
        for line in takewhile(lambda x: len(x) > 0, lines[l:]):
            self.events.append(Event(line.split('\t'), self.header))
        self.subjectID = self.events[0].data['Subject']

    def segment(self, smarker, emarker):
        self.segments = []
        inblock = False
        for item in self.events:
            if item.code == smarker:
                inblock = True
                self.segments.append([])
            elif item.code == emarker:
                if not inblock:
                    print('Warning: found end block before start block')
                inblock = False
            elif inblock:
                self.segments[-1].append(item)


def load(f):
    '''Load a file and create the resulting Record object'''
    return Record(f)


def subset(n, builder):
    '''Create a Measure with name n and builder function'''
    m = Measure(n)
    m.build = builder
    return m
