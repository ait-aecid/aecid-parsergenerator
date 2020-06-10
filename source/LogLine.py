class LogLine:
    """This class describes log lines"""
    def __init__(self, line_id, time_stamp, line_text, words):
        self.line_id = line_id
        self.time_stamp = time_stamp
        self.line_text = line_text
        self.words = words
        self.cluster = ''
