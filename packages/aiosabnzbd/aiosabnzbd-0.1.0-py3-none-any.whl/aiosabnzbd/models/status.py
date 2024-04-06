"""Models for operational APIs."""
from dataclasses import dataclass

from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass(frozen=True, kw_only=True, slots=True)
class StatusResponse(DataClassORJSONMixin):
    """Response from the API."""

    status: bool
