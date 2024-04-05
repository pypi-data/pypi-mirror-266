from web.dto import CommonDto


class ProcessingException(Exception):
    def __init__(self, message):
        self.message = message


class RestException(CommonDto):
    type: str
    message: str = Field(None)
    details: [dict] = Field(None)
