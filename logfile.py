from __future__ import division
from exceptions import LoadError
from datetime import datetime
import os

class Experiment:
    def __init__(self, name):
        self.name = name


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
        #Grab Scenario name
        if lines[0].split('-')[0].strip() == 'Scenario':
            self.exp = Experiment(lines[0].split('-')[1].strip())
        else:
            raise LoadError('Err: first line does not start with Scenario')
        #Get Logfile timestamp
        if lines[1].split('-')[0].strip() == 'Logfile written':
            self.timestamp = datetime.strptime(lines[1].split('-')[1].strip(),
                                               '%m/%d/%Y %H:%M:%S')
        else:
            raise LoadError('Err: second line does not contain timestamp')

    def segment(smarker, emarker):
        pass

def load(f):
    return Record(f)
