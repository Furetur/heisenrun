from enum import StrEnum


class Status(StrEnum):
    NOT_STARTED = "NOT STARTED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    TIMEOUT = "TIMEOUT"
    INTERRUPTED = "INTERRUPTED"
