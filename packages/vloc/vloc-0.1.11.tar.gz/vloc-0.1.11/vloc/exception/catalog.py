class AiDetectException(Exception):

    def __init__(self,  message: str):
        self.message = message


class OcrException(Exception):

    def __init__(self,  message: str):
        self.message = message
