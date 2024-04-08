from enum import Enum, auto

class Event(Enum):
    AGENT_INIT = "AGENT_INIT"
    POLL = "POLL"
    VALIDATE = "VALIDATE"
    VALIDATE_ERROR = "VALIDATE_ERROR"
    SHUTDOWN = "SHUTDOWN"
    UPLOAD_S3 = "UPLOAD_S3"
    GPT = "GPT"