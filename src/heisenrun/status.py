from enum import Enum


class Status(str, Enum):
    NOT_STARTED = "NOT STARTED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    TIMEOUT = "TIMEOUT"
    INTERRUPTED = "INTERRUPTED"
