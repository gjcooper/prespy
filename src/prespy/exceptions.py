class LoadError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DataNotFoundError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


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
