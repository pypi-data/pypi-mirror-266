from __future__ import annotations

import datetime
import logging
import uuid
from typing import TYPE_CHECKING, List, Optional, Sequence, Union

from langmem.client import AsyncClient as AsyncLangMemClient
from langmem.client import Client as LangMemClient
import importlib.util

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from langchain_core.chat_history import BaseChatMessageHistory
    from langchain_core.messages import BaseMessage
else:
    try:
        from langchain_core.chat_history import BaseChatMessageHistory
    except ImportError:
        logger.debug("langchain_core not installed. Skipping import.")
        BaseChatMessageHistory = object


def _try_import():
    try:
        importlib.util.find_spec("langchain_community.adapters.openai")
    except ImportError:
        raise ImportError(
            "To use LangMemChatMessageHistory, you must have langchain_community installed."
            "You can install it with `pip install langchain-community`."
        )


def _convert_message_to_dict_enhanced(msg: BaseMessage) -> dict:
    from langchain_community.adapters.openai import convert_message_to_dict  # type: ignore[import]

    d = convert_message_to_dict(msg)
    if not d.get("name") and msg.name:
        d["name"] = msg.name
    metadata = d.setdefault("metadata", {}) or {}
    metadata.update(msg.additional_kwargs)
    d["metadata"] = metadata
    if "timestamp" not in d:
        d["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return d


class LangMemChatMessageHistory(BaseChatMessageHistory):
    """Chat message history stored using LangMem."""

    def __init__(
        self,
        thread_id: Union[str, uuid.UUID],
        sync_client: Optional[LangMemClient] = None,
        async_client: Optional[AsyncLangMemClient] = None,
    ):
        _try_import()
        self.thread_id = str(thread_id)
        self.sync_client = sync_client or LangMemClient()
        self.async_client = async_client or AsyncLangMemClient()

    @property
    def key(self) -> str:
        """Construct the record key to use."""
        return f"chat_history:{self.thread_id}"

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore[override]
        """Retrieve the messages from LangMem (synchronously)."""
        from langchain_community.adapters.openai import convert_dict_to_message

        messages = [
            convert_dict_to_message(msg)
            for msg in self.sync_client.list_messages(thread_id=self.thread_id)
        ]
        return messages

    async def alist_messages(self) -> List[BaseMessage]:
        """Retrieve the messages from LangMem (asynchronously)."""
        from langchain_community.adapters.openai import convert_dict_to_message  # type: ignore[import]

        gen = self.async_client.list_messages(thread_id=self.thread_id)
        retrieved_messages = []
        async for msg in gen:
            retrieved_messages.append(convert_dict_to_message(msg))
        return retrieved_messages

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """Add a list of messages (synchronously)."""
        new_messages = [_convert_message_to_dict_enhanced(m) for m in messages]
        self.sync_client.add_messages(thread_id=self.thread_id, messages=new_messages)

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        """Add a list of messages (asynchronously)."""
        new_messages = [_convert_message_to_dict_enhanced(m) for m in messages]
        await self.async_client.add_messages(
            thread_id=self.thread_id, messages=new_messages
        )

    def clear(self) -> None:
        """Clear the chat history (synchronously)."""
        raise NotImplementedError()

    async def aclear(self) -> None:
        """Clear the chat history (asynchronously)."""
        raise NotImplementedError()

    def end(self) -> None:
        """End the chat history (synchronously)."""
        return self.sync_client.trigger_all_for_thread(thread_id=self.thread_id)

    async def aend(self) -> None:
        """End the chat history (asynchronously)."""
        return await self.async_client.trigger_all_for_thread(thread_id=self.thread_id)
