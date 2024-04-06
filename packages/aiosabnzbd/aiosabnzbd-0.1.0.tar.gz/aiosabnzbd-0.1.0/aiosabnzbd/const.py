"""Constants for aiosabnzbd."""

from enum import StrEnum


class QueueStatus(StrEnum):
    """Enum for queue status."""

    IDLE = "Idle"
    QUEUED = "Queued"
    PAUSED = "Paused"
    DOWNLOADING = "Downloading"
    PROPAGATING = "Propagating"
    FETCHING = "Fetching"


class QueueOperationCommand(StrEnum):
    """Enum for queue operation command."""

    RESUME = "resume"
    PAUSE = "pause"
