from typing import Any, Dict, Union
from typing_extensions import TypedDict

from typing import List, Optional
from datetime import datetime
import uuid


class GetThreadStateResponse(TypedDict, total=False):
    """
    Represents a response for a thread state.

    Attributes:
        state (Dict[str, Any]): The state of the thread.
    """

    state: Dict[str, Any]


class UserMetadata(TypedDict, total=False):
    """
    Represents metadata for a user.

    Attributes:
        user_id (Optional[uuid.UUID]): The unique identifier of the user.
        user_name (Optional[str]): The name of the user.
    """

    user_id: Optional[uuid.UUID]
    user_name: Optional[str]


class UserForMessage(UserMetadata, total=False):
    """
    Represents a user for a message.

    Attributes:
        role (str): The role of the user in the message.
    """

    role: str


class Metadata(UserMetadata, total=False):
    """Metadata.
    
    Represents metadata for a message. Used to help associate and deduplicate
    memories.

    Attributes:
        timestamp (Optional[datetime]): The timestamp of the message.
    """

    timestamp: Optional[datetime]


class OpenAIMessage(TypedDict, total=False):
    """OpenAI Message.
    
    Represents an OpenAI message, with optional user metadata to direct
    LangMem to process memories for the user.

    Attributes:
        content (str | List[dict]): The content of the message.
        role (str): The role of the message sender.
        name (Optional[str]): The name of the message sender.
        metadata (Optional[Union[Metadata, Dict[str, Any]]]): Additional metadata for the message.
    """

    content: str | List[dict]
    role: str
    name: Optional[str]
    metadata: Optional[Union[Metadata, Dict[str, Any]]]


class Message(TypedDict, total=False):
    """LangMem Message.

    Represents a message.

    Attributes:
        id (uuid.UUID): The unique identifier of the message.
        content (str | List[Dict[str, Any]]): The content of the message.
        timestamp (datetime): The timestamp of the message.
        user (UserForMessage): The user associated with the message.
    """

    id: uuid.UUID
    content: str | List[Dict[str, Any]]
    timestamp: datetime
    user: UserForMessage


MESSAGE_LIKE = Union[OpenAIMessage, Message]
"""
Represents a message-like object, which can be either an OpenAIMessage or a Message.
"""
