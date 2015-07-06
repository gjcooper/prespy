from __future__ import division
from exceptions import LoadError
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
        #Grab Scenario name
        if lines[l].split('-')[0].strip() == 'Scenario':
            self.exp = Experiment(lines[l].split('-')[1].strip())
            l += 1
        else:
            raise LoadError('Err: first line does not start with Scenario')
        #Get Logfile timestamp
        if lines[l].split('-')[0].strip() == 'Logfile written':
            self.timestamp = datetime.strptime(lines[l].split('-')[1].strip(),
                                               '%m/%d/%Y %H:%M:%S')
            l += 1
        else:
            raise LoadError('Err: second line does not contain timestamp')
        #Grab Logfile Header
        for line in lines[l:]:
            if line.startswith('Subject'):
                self.header = line.split('\t')
                l += 1
                break
            else:
                l += 1
        if lines[l] != '':
            raise LoadError('Err: Expected blank line between header and body')
        self.codecol = self.header.index('Code')
        self.timecol = self.header.index('Time')
        self.typecol = self.header.index('Event Type')
        self.durcol = self.header.index('Duration')
        self.rstatcol = self.header.index('Stim Type')
        #Grab data
        l += 1
        self.data = []
        for line in takewhile(lambda x: len(x) > 0, lines[l:]):
            self.data.append(line.split('\t'))
        self.subjectID = self.data[0][self.header.index('Subject')]


    def segment(self, smarker, emarker):
        self.segments = []
        inblock = False
        for item in self.data:
            code = item[self.header.index('Code')]
            if code == smarker:
                inblock = True
                self.segments.append([])
            elif code == emarker:
                if not inblock:
                    raise LoadError('Err: found end block before start block')
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

