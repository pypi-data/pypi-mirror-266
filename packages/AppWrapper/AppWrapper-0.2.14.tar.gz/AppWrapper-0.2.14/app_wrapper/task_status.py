from enum import Enum


class Status(str, Enum):
    Complete = "Complete"
    Processing = "Processing"
    Failed = "Failed"
    Canceled = "Canceled"
    Scheduled = "Scheduled"
    Paused = "Paused"
