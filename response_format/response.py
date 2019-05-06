class ResponseFormat(object):
    def __init__(self, ids, count, message,error_code):
        self.ids = ids
        self.count = count
        self.message = message
        self.error_code = error_code

