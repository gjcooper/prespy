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
