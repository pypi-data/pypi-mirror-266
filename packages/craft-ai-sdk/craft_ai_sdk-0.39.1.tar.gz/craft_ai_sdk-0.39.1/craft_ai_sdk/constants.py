from strenum import LowercaseStrEnum
from enum import auto


class DEPLOYMENT_EXECUTION_RULES(LowercaseStrEnum):

    """Enumeration for deployments execution rules."""

    ENDPOINT = auto()
    PERIODIC = auto()


class DEPLOYMENT_MODES(LowercaseStrEnum):

    """Enumeration for deployments modes."""

    LOW_LATENCY = auto()
    ELASTIC = auto()


class DEPLOYMENT_UPDATE_STATUS(LowercaseStrEnum):

    """Enumeration for deployments update status."""

    CREATING = auto()
    UPDATING = auto()
    SUCCESS = auto()
    FAILED = auto()


CREATION_REQUESTS_RETRY_INTERVAL = 10
