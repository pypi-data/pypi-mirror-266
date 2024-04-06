"""Models for the SABnzbd queue API."""
from dataclasses import dataclass, field

from mashumaro.mixins.orjson import DataClassORJSONMixin

from aiosabnzbd.const import QueueOperationCommand, QueueStatus

from .base import SabnzbdRequest


@dataclass(frozen=True, kw_only=True, slots=True)
class Slot:
    """Representation of a download slot in the queue."""

    status: QueueStatus
    index: int
    password: str
    avg_age: str
    script: str
    direct_unpack: str
    mb: str
    mb_left: str = field(metadata={"alias": "mbleft"})
    mb_missing: str = field(metadata={"alias": "mbmissing"})
    size: str
    size_left: str = field(metadata={"alias": "sizeleft"})
    filename: str
    labels: list[str]
    priority: str
    cat: str
    timeleft: str
    percentage: str
    nzo_id: str
    unpack_opts: str = field(metadata={"alias": "unpackopts"})


@dataclass(frozen=True, kw_only=True, slots=True)
class Queue(DataClassORJSONMixin):
    """Representation the queue."""

    status: QueueStatus
    speedlimit: str
    speedlimit_absolut: str = field(metadata={"alias": "speedlimit_abs"})
    paused: bool
    noofslots_total: int
    noofslots: int
    limit: int
    start: int
    timeleft: str
    speed: str
    kb_per_sec: str = field(metadata={"alias": "kbpersec"})
    size: str
    size_left: str = field(metadata={"alias": "sizeleft"})
    megabyte: str = field(metadata={"alias": "mb"})
    megabyte_left: str = field(metadata={"alias": "mbleft"})
    slots: list[Slot]
    diskspace1: str
    diskspace2: str
    diskspace_total1: str = field(metadata={"alias": "diskspacetotal1"})
    diskspace_total2: str = field(metadata={"alias": "diskspacetotal2"})
    diskspace1_norm: str
    diskspace2_norm: str
    have_warnings: str
    pause_int: str
    left_quota: str
    version: str
    finish: int
    cache_article: str = field(metadata={"alias": "cache_art"})
    cache_size: str
    finish_action: str = field(metadata={"alias": "finishaction"})
    paused_all: bool
    quota: str
    have_quota: bool


@dataclass(frozen=True, kw_only=True, slots=True)
class QueueResponse(DataClassORJSONMixin):
    """Queue API response."""

    queue: Queue


@dataclass(kw_only=True)
class QueueRequest(SabnzbdRequest):
    """Request to get the latest queue data."""

    @property
    def query_params(self) -> dict[str, str]:
        """Return the query parameters."""
        return {"mode": "queue"}


@dataclass(kw_only=True)
class QueueOperationRequest(SabnzbdRequest):
    """Request to perform a queue operation."""

    mode: QueueOperationCommand

    @property
    def query_params(self) -> dict[str, str]:
        """Return the query parameters."""
        return {"mode": self.mode}
