class LocationTypeError(Exception):
    def __init__(self, val, msg, location=None):
        self.val = val
        self.msg = msg
        self.location = location
        super().__init__()

    def __str__(self):
        return "{} - {} --> {}".format(self.msg, self.val, self.location)


class RequestError(Exception):
    def __init__(self, val, err, msg=None, retry=None):
        self.val = val
        self.err = err
        self.msg = msg
        self.retry = retry or 0
        super().__init__()

    def __str__(self):
        return "{} - {} 请求 {} 次失败 --> {}".format(self.msg, self.val, self.retry, self.err)
