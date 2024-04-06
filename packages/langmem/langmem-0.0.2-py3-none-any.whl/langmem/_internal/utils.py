from typing import Union
import uuid

# Client for the following API:
ID_T = Union[uuid.UUID, str]


def as_uuid(value: ID_T) -> uuid.UUID:
    return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
