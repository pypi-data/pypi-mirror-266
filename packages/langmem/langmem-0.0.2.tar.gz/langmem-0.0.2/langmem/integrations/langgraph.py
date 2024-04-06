from __future__ import annotations

import json
import logging
import uuid
import warnings
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, TypedDict

from langmem.client import AsyncClient as AsyncLangMemClient
from langmem.client import Client as LangMemClient

if TYPE_CHECKING:
    from langgraph.checkpoint.base import (  # type: ignore[import]
        BaseCheckpointSaver,
        Checkpoint,
    )
try:
    from langchain_core.messages import BaseMessage  # type: ignore[import]
    from langchain_core.pydantic_v1 import Field  # type: ignore[import]
    from langchain_core.runnables import (  # type: ignore[import]
        ConfigurableFieldSpec,
        RunnableConfig,
    )
    from langgraph.checkpoint.base import (  # type: ignore[import]
        BaseCheckpointSaver,
        Checkpoint,
    )
except Exception:
    from pydantic import BaseModel, Field  # type: ignore[assignment]

    BaseCheckpointSaver = BaseModel  # type: ignore[misc, assignment]


logger = logging.getLogger(__name__)


def _deserialize_checkpoint(serialized: dict) -> Checkpoint:
    from langchain_core.load import load  # type: ignore[import]

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        loaded = load(serialized, valid_namespaces=["uuid"])
    loaded["channel_versions"] = defaultdict(int, loaded["channel_versions"])
    loaded["versions_seen"] = defaultdict(
        lambda: defaultdict(int), loaded["versions_seen"]
    )
    return loaded


def _serialize_checkpoint(checkpoint: Checkpoint) -> dict:
    from langchain_core.load import dump  # type: ignore[import]

    return json.loads(dump.dumps(checkpoint))


# Yet another message format
class UserInfo(TypedDict):
    user_id: Optional[uuid.UUID]
    user_name: Optional[str]


def _default_lookup_user_info(message: BaseMessage) -> UserInfo:
    return {
        "user_id": message.additional_kwargs.get("user_id"),
        "user_name": message.additional_kwargs.get("user_name"),
    }


def message_to_dict(
    message: BaseMessage, lookup_user_info: Callable[[BaseMessage], UserInfo]
) -> dict:
    """Convert a Message to a dictionary.

    Args:
        message: Message to convert.

    Returns:
        Message as a dict.
    """
    mtype = message.type
    role = {"human": "user", "ai": "assistant"}.get(mtype, mtype)
    message_dict: Dict[str, Any] = {
        "content": message.content,
        "role": role,
    }
    if message.type == "human":
        user_info = lookup_user_info(message)
        message_dict["metadata"] = {
            "user_name": user_info.get("user_name"),
            "user_id": str(user_info["user_id"]) if user_info["user_id"] else None,
        }

    return message_dict


def _convert_messages(
    messages: List[BaseMessage],
    lookup_user_info: Callable[[BaseMessage], UserInfo] = _default_lookup_user_info,
) -> List[dict]:
    return [message_to_dict(m, lookup_user_info) for m in messages]


class _ThreadStateKwargs(TypedDict):
    thread_id: uuid.UUID
    key: str


class MessagesCheckpoint(BaseCheckpointSaver):
    aclient: AsyncLangMemClient = Field(default_factory=AsyncLangMemClient)
    client: LangMemClient = Field(default_factory=LangMemClient)
    serialize_checkpoint: Callable[[Checkpoint], dict] = Field(
        default=_serialize_checkpoint
    )
    deserialize_checkpoint: Callable[[dict], Checkpoint] = Field(
        default=_deserialize_checkpoint
    )
    convert_messages: Callable[[List[BaseMessage]], List[dict]] = Field(
        default=_convert_messages
    )

    class Config:
        arbitrary_types_allowed = True

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        from langchain_core.runnables import ConfigurableFieldSpec

        return [
            ConfigurableFieldSpec(
                id="thread_id",
                annotation=uuid.UUID,
                name="Thread ID",
                description=None,
                is_shared=True,
            ),
            ConfigurableFieldSpec(
                id="checkpoint_key",
                annotation=str,
                name="Checkpoint Key",
                description="""The key to save this graph's checkpoint under within a thread pair.
                
                Used when there are multiple graphs operating on a single thread.
                """,
            ),
        ]

    def _get_thread_ids(self, config: RunnableConfig) -> _ThreadStateKwargs:
        configurable = config.get("configurable") or {}
        return {
            "thread_id": configurable["thread_id"],
            "key": configurable.get("checkpoint_key") or "checkpoint",
        }

    def get(self, config: RunnableConfig) -> Optional[Checkpoint]:
        thread_state_kwargs = self._get_thread_ids(config)
        state_response = self.client.get_thread_state(**thread_state_kwargs)
        state = state_response.get("state")
        logger.debug("Got state: %s", state)
        if state is None:
            return None
        return self.deserialize_checkpoint(state)

    def put(self, config: RunnableConfig, checkpoint: Checkpoint) -> RunnableConfig:
        from langgraph.graph import END  # type: ignore[import]

        thread_state_kwargs = self._get_thread_ids(config)
        response: RunnableConfig = {
            "configurable": {
                "thread_id": thread_state_kwargs["thread_id"],
                "checkpoint_key": thread_state_kwargs["key"],
            }
        }
        serialized = self.serialize_checkpoint(checkpoint)
        self.client.add_thread_state(
            **thread_state_kwargs,
            state=serialized,
        )
        channel_values = checkpoint["channel_values"]
        if END in channel_values:
            messages = channel_values[END]
            if not (
                isinstance(messages, list)
                and all([isinstance(m, BaseMessage) for m in messages])
            ):
                logger.warning(
                    "MessagesCheckpoint received non-messagegraph checkpoint data"
                    "Skipping memory store update."
                )
                return response
            converted = self.convert_messages(messages)
            logger.debug("Adding messages: %s", converted)
            self.client.add_messages(
                thread_id=thread_state_kwargs["thread_id"],
                messages=converted,
            )
        return response

    async def aget(self, config: RunnableConfig) -> Optional[Checkpoint]:
        thread_state_kwargs = self._get_thread_ids(config)
        state_response = await self.aclient.get_thread_state(**thread_state_kwargs)
        state = state_response.get("state")
        logger.debug("Got state: %s", state)
        if state is None:
            return None
        return self.deserialize_checkpoint(state)

    async def aput(
        self, config: RunnableConfig, checkpoint: Checkpoint
    ) -> RunnableConfig:
        from langgraph.graph import END  # type: ignore[import]

        thread_state_kwargs = self._get_thread_ids(config)
        response: RunnableConfig = {
            "configurable": {
                "thread_id": thread_state_kwargs["thread_id"],
                "checkpoint_key": thread_state_kwargs["key"],
            }
        }
        serialized = self.serialize_checkpoint(checkpoint)
        await self.aclient.add_thread_state(
            **thread_state_kwargs,
            state=serialized,
        )
        channel_values = checkpoint["channel_values"]
        if END in channel_values:
            messages = channel_values[END]
            if not (
                isinstance(messages, list)
                and all([isinstance(m, BaseMessage) for m in messages])
            ):
                logger.warning(
                    "MessagesCheckpoint received non-messagegraph checkpoint data"
                    "Skipping memory store update."
                )
                return response
            converted = self.convert_messages(messages)
            logger.debug("Adding messages: %s", converted)
            await self.aclient.add_messages(
                thread_id=thread_state_kwargs["thread_id"],
                messages=converted,
            )
        return response
