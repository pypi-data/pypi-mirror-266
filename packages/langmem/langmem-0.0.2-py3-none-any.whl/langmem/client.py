import datetime
import json
import os
import uuid
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
)

import httpx
from langmem._internal.utils import ID_T
from langmem._internal.utils import as_uuid as _as_uuid
from langmem import schemas
from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1

DEFAULT_TIMEOUT = httpx.Timeout(timeout=30.0, connect=10.0)


def _ensure_url(url: Optional[str]) -> str:
    url_ = url or os.environ.get("LANGMEM_API_URL")
    if url_ is None:
        raise ValueError(
            "api_url is required. Please set LANGMEM_API_URL "
            "or manually provided it to the client."
        )
    return url_


def _default_serializer(obj: Any) -> str:
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, BaseModel):
        return json.loads(obj.model_dump_json())
    if isinstance(obj, BaseModelV1):
        return json.loads(obj.json())
    return json.loads(json.dumps(obj, default=_default_serializer))


def raise_for_status_with_text(response: httpx.Response) -> None:
    """Raise an error with the response text."""
    try:
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise httpx.HTTPError(f"{str(e)}: {response.text}") from e


class AsyncClient:
    """The Async Langmem client.

    Examples:

        Basic usage:

            >>> from langmem import AsyncClient
            >>> from pydantic import BaseModel, Field
            >>> client = AsyncClient()
            >>> class UserProfile(BaseModel):
            ...     name: str = Field(description="The user's name")
            ...     age: int = Field(description="The user's age")
            ...     interests: List[str] = Field(description="The user's interests")
            ...     relationships: Dict[str, str] = Field(
            ...         description="The user's friends, family, pets,and other relationships."
            ...     )
            >>> memory_function = await client.create_memory_function(
            ...     UserProfile,
            ...     target_type="user_state",
            ...     name="User Profile",
            ... )
            >>> user_id = uuid.uuid4()
            >>> user_name = "Will"
            >>> messages = [
            ...     {
            ...         "role": "user",
            ...         "content": "Did you know pikas make their own haypiles?",
            ...         "name": "Will",
            ...         "metadata": {"user_id": user_id},
            ...     },
            ...     {
            ...         "role": "assistant",
            ...         "content": "Yes! And did you know they're actually related to rabbits?",
            ...     },
            ...     {
            ...         "role": "user",
            ...         "content": "I did! More people should know this important knowledge.",
            ...         "name": "Will",
            ...         "metadata": {"user_id": user_id},
            ...     },
            ... ]
            >>> thread_id = uuid.uuid4()
            >>> await client.add_messages(thread_id, messages)
            >>> await client.trigger_all_for_thread(thread_id)
            >>> await client.get_user_memory(user_id, memory_function_id=memory_function["id"])
            >>> # Or query the unstructured memory
            >>> await client.query_user_memory(user_id, "pikas", k=1)

            Query user memories semantically:

            >>> await client.query_user_memory(
            ...     user_id=user_id,
            ...     text="What does the user think about rabbits?",
            ...     memory_function_ids=[belief_function["id"]],
            ...     k=3,
            ... )

            Create a thread summary memory function:

            >>> class ConversationSummary(BaseModel):
            ...     title: str = Field(description="Distinct for the conversation.")
            ...     summary: str = Field(description="High level summary of the interactions.")
            ...     topic: List[str] = Field(
            ...         description="Tags for topics discussed in this conversation."
            ...     )
            >>> thread_summary_function = await client.create_memory_function(
            ...     ConversationSummary, target_type="thread_summary"
            ... )

            Fetch thread messages:

            >>> messages = client.list_messages(thread_id=thread_id)
            >>> async for message in messages:
            ...     print(message)
    """

    __slots__ = ["api_key", "client"]

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("LANGMEM_API_KEY")
        base_url = _ensure_url(api_url)
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers=self._headers,
            timeout=DEFAULT_TIMEOUT,
        )

    @property
    def _headers(self):
        if self.api_key is None:
            return {}
        return {
            "x-api-key": self.api_key,
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.client.aclose()

    async def create_user(
        self,
        *,
        user_id: ID_T,
        name: str,
        tags: Optional[Sequence[str]] = None,
        metadata: Dict[str, str] = {},
    ) -> Dict[str, Any]:
        """Create a user.

        Args:
            user_id (ID_T): The user's ID.
            name (str): The user's name.
            tags (Optional[Sequence[str]], optional): The user's tags. Defaults to None.
            metadata (Dict[str, str], optional): The user's metadata. Defaults to {}.

        Returns:
            Dict[str, Any]: The user's data.
        """

        data = {
            "id": user_id,
            "name": name,
            "tags": tags,
            "metadata": metadata,
        }
        response = await self.client.post("/users", json=data)

        return response.json()

    async def get_user(self, user_id: ID_T) -> Dict[str, Any]:
        """Get a user.

        Args:
            user_id (ID_T): The user's ID.

        Returns:
            Dict[str, Any]: The user's data.
        """

        response = await self.client.get(f"/users/{_as_uuid(user_id)}")
        raise_for_status_with_text(response)
        return response.json()

    async def update_user(
        self,
        user_id: ID_T,
        *,
        name: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Update a user.

        Args:
            user_id (ID_T): The user's ID.
            name (Optional[str], optional): The user's name. Defaults to None.
            tags (Optional[Sequence[str]], optional): The user's tags. Defaults to None.
            metadata (Optional[Dict[str, str]], optional): The user's metadata. Defaults to None.

        Returns:
            Dict[str, Any]: The user's data.
        """

        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if tags is not None:
            data["tags"] = tags
        if metadata is not None:
            data["metadata"] = metadata
        response = await self.client.patch(f"/users/{_as_uuid(user_id)}", json=data)
        raise_for_status_with_text(response)
        return response.json()

    async def list_users(
        self,
        *,
        name: Optional[Sequence[str]] = None,
        id: Optional[Sequence[ID_T]] = None,
    ) -> List[Dict[str, Any]]:
        """List users.

        Args:
            name (Optional[Sequence[str]], optional): The user's name. Defaults to None.
            id (Optional[Sequence[ID_T]], optional): The user's ID. Defaults to None.

        Returns:
            List[Dict[str, Any]]: The users' data.
        """

        params = {
            "name": name,
            "id": id,
        }

        response = await self.client.post(
            "/users/query",
            json=params,
            headers={"Content-Type": "application/json"},
        )
        raise_for_status_with_text(response)
        return response.json()["users"]

    async def list_user_memory(self, user_id: ID_T) -> List[Dict[str, Any]]:
        """List a user's memory.

        Args:
            user_id (ID_T): The user's ID.

        Returns:
            List[Dict[str, Any]]: The user's memory.
        """

        response = await self.client.get(f"/users/{_as_uuid(user_id)}/memory")
        raise_for_status_with_text(response)
        return response.json()

    async def trigger_all_for_user(self, user_id: ID_T) -> None:
        """Trigger all memory functions for a user.

        Args:
            user_id (ID_T): The user's ID.
        """

        response = await self.client.post(f"/users/{_as_uuid(user_id)}/trigger-all")
        raise_for_status_with_text(response)
        return response.json()

    async def delete_user_memory(
        self,
        *,
        user_id: ID_T,
        memory_function_id: ID_T,
    ) -> None:
        """Delete a user's memory.

        Args:
            user_id (ID_T): The user's ID.
            memory_function_id (ID_T): The memory function's ID.
        """

        response = await self.client.delete(
            f"/users/{_as_uuid(user_id)}/memory/{_as_uuid(memory_function_id)}/state"
        )
        raise_for_status_with_text(response)
        return response.json()

    async def update_user_memory(
        self,
        user_id: ID_T,
        *,
        memory_function_id: ID_T,
        state: dict,
    ) -> None:
        """Update a user's memory.

        Args:
            user_id (ID_T): The user's ID.
            memory_function_id (ID_T): The memory function's ID.
            state (dict): The memory state.
        """
        response = await self.client.put(
            f"/users/{_as_uuid(user_id)}/memory/{_as_uuid(memory_function_id)}/state",
            data=json.dumps(  # type: ignore[arg-type]
                {"state": state},
                default=_default_serializer,
            ),
        )
        raise_for_status_with_text(response)
        return response.json()

    async def get_user_memory(
        self,
        user_id: ID_T,
        *,
        memory_function_id: ID_T,
    ) -> dict:
        """Get a user's memory state.

        This method retrieves the current memory state for a specific user and memory function.
        It is faster than querying and useful for "user_state" type memories.

        Args:
            user_id (ID_T): The user's ID.
            memory_function_id (ID_T): The memory function's ID.

        Returns:
            dict: The memory state.

        Examples:

            >>> from langmem import AsyncClient
            >>> client = AsyncClient()
            >>> user_id = "2d1a8daf-2319-4e3e-9fd0-6d7981ceb8a6"
            >>> memory_function_id = "cb217ff7-963e-44fc-b222-01f01058d64b"
            >>> await client.get_user_memory(user_id, memory_function_id=memory_function_id)
        """
        response = await self.client.get(
            f"/users/{_as_uuid(user_id)}/memory/{_as_uuid(memory_function_id)}/state"
        )
        raise_for_status_with_text(response)
        return response.json()

    async def query_user_memory(
        self,
        user_id: ID_T,
        text: str,
        k: int = 200,
        memory_function_ids: Optional[Sequence[ID_T]] = None,
        weights: Optional[dict] = None,
        states_to_return: Optional[Sequence[ID_T]] = None,
        thread_summaries: Optional[Sequence[ID_T]] = None,
        thread_summaries_k: Optional[int] = None,
    ) -> List:
        """Query a user's memory.

        Args:
            user_id (ID_T): The user's ID.
            text (str): The query text.
            k (int, optional): The number of results to return. Defaults to 200.
            memory_function_ids (Optional[Sequence[ID_T]], optional): Semantic memory outputs
                    to include. Defaults to None, meaning just the unstructured memories.
            weights (Optional[dict], optional): Weights for the different memory types.
                    Backend default equally weights relevance, recency, and importance.
                    Defaults to None.
            states_to_return (Optional[Sequence[ID_T]], optional): The user state
                    memory function IDs to include in the response.
            thread_summaries (Optional[Sequence[ID_T]], optional): The thread
                    summary memory function IDs to include in the response, if any.
            thread_summaries_k (Optional[int], optional): If you include thread summaries,
                this controls the number of threads whose summaries you wish to return per
                thread summary memory function. Defaults to None.

        Returns:
            List: The query results.


        Examples:

            Query a user's semantic memory:
                >>> from langmem import AsyncClient
                >>> client = AsyncClient()
                >>> user_id = uuid.uuid4()
                >>> await client.query_user_memory(user_id, text="pikas", k=10)

            Query the memory, ignoring recency or perceived importance:

                >>> await client.query_user_memory(
                ...     user_id,
                ...     text="pikas",
                ...     k=10,
                ...     weights={"relevance": 1.0, "recency": 0.0, "importance": 0.0},
                ... )

            Include user state memories in the response (to save the number of API calls):
                >>> mem_functions_ = client.list_memory_functions(target_type="user")
                >>> mem_functions = []
                >>> async for mem_function in mem_functions_:
                ...     if mem_function["type"] == "user_state":
                ...         mem_functions.append(mem_function["id"])
                >>> await client.query_user_memory(
                ...     user_id,
                ...     text="pikas",
                ...     k=10,
                ...     states_to_return=mem_functions,
                ... )

            Query over user_append_state memories:
                >>> mem_functions_ = client.list_memory_functions(target_type="user")
                >>> mem_functions = []
                >>> async for mem_function in mem_functions_:
                ...     if mem_function["type"] == "user_append_state":
                ...         mem_functions.append(mem_function["id"])
                >>> await client.query_user_memory(
                ...     user_id,
                ...     text="pikas",
                ...     k=10,
                ...     memory_function_ids=mem_functions,
                ... )

            Include thread summaries for the most recent threads:
                >>> mem_functions_ = client.list_memory_functions(target_type="thread")
                >>> mem_functions = []
                >>> async for mem_function in mem_functions_:
                ...     mem_functions.append(mem_function["id"])
                >>> await client.query_user_memory(
                ...     user_id,
                ...     text="pikas",
                ...     k=10,
                ...     thread_summaries=mem_functions,
                ...     thread_summaries_k=5,
                ... )

        """
        thread_query = None
        if thread_summaries is not None:
            thread_query: dict = {
                "memory_function_ids": thread_summaries,
            }
            if thread_summaries_k is not None:
                thread_query["k"] = thread_summaries_k

        response = await self.client.post(
            f"/users/{_as_uuid(user_id)}/memory/query",
            data=json.dumps(  # type: ignore[arg-type]
                {
                    "text": text,
                    "k": k,
                    "memory_function_ids": memory_function_ids,
                    "weights": weights,
                    "state": states_to_return,
                },
                default=_default_serializer,
            ),
        )
        raise_for_status_with_text(response)
        return response.json()

    async def create_memory_function(
        self,
        parameters: Union[BaseModel, dict],
        *,
        target_type: str = "user_state",
        name: Optional[str] = None,
        description: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        function_id: Optional[ID_T] = None,
    ) -> Dict[str, Any]:
        """Create a memory function.

        Args:
            parameters (Union[BaseModel, dict]): The memory function's parameters.
            target_type (str, optional): The memory function's target type. Defaults to "user_state".
            name (Optional[str], optional): The memory function's name. Defaults to None.
            description (Optional[str], optional): The memory function's description. Defaults to None.
            custom_instructions (Optional[str], optional): The memory function's custom instructions. Defaults to None.
            function_id (Optional[ID_T], optional): The memory function's ID. Defaults to None.

        Returns:
            Dict[str, Any]: The memory function's data.

        Examples:

            Create a user profile memory function:

                >>> from pydantic import BaseModel, Field
                >>> from langmem import Client
                >>> client = AsyncClient()
                >>> class UserProfile(BaseModel):
                ...     name: str = Field(description="The user's name")
                ...     age: int = Field(description="The user's age")
                ...     interests: List[str] = Field(description="The user's interests")
                ...     relationships: Dict[str, str] = Field(
                ...         description="The user's friends, family, pets,and other relationships."
                ...     )
                >>> memory_function = await client.create_memory_function(
                ...     UserProfile,
                ...     target_type="user_state",
                ...     name="User Profile",
                ... )

            Create an append-only user memory function:

                >>> class FormativeEvent(BaseModel):
                ...     event: str = Field(description="The formative event that occurred.")
                ...     impact: str = Field(description="How this event impacted the user.")
                >>> event_function = await client.create_memory_function(
                ...     FormativeEvent, target_type="user_append_state"
                ... )

        """
        if isinstance(parameters, dict):
            params: dict = parameters

        else:
            params = parameters.model_json_schema()

        function_schema = {
            "name": name or params.pop("title", ""),
            "description": description or params.pop("description", ""),
            "parameters": params,
        }

        data = {
            "type": target_type,
            "custom_instructions": custom_instructions,
            "id": str(function_id) if function_id else str(uuid.uuid4()),
            "schema": function_schema,
        }
        response = await self.client.post("/memory-functions", json=data)
        raise_for_status_with_text(response)
        return response.json()

    async def get_memory_function(self, memory_function_id: ID_T) -> Dict[str, Any]:
        """Get a memory function.

        Args:
            memory_function_id (ID_T): The memory function's ID.

        Returns:
            Dict[str, Any]: The memory function's data.
        """

        response = await self.client.get(
            f"/memory-functions/{_as_uuid(memory_function_id)}"
        )
        raise_for_status_with_text(response)
        return response.json()

    async def list_memory_functions(
        self, *, target_type: Optional[Sequence[str]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """List memory functions.

        Args:
            target_type (Sequence[str], optional): The memory function's target type. Defaults to None.

        Returns:
            AsyncGenerator[Dict[str, Any], None]: The memory functions' data.
        """

        body = {}
        if target_type is not None:
            body["target_type"] = (
                [target_type] if isinstance(target_type, str) else target_type
            )
        cursor = None
        while True:
            if cursor is not None:
                body["cursor"] = cursor
            response = await self.client.post("/memory-functions/query", json=body)
            raise_for_status_with_text(response)
            data = response.json()
            for function in data.get("memory_functions", []):
                yield function
            cursor = data.get("next_cursor")
            if cursor is None:
                break

    async def update_memory_function(
        self,
        memory_function_id: ID_T,
        *,
        name: Optional[str] = None,
        schema: Optional[Union[BaseModel, dict]] = None,
        custom_instructions: Optional[str] = None,
        description: Optional[str] = None,
        function_type: Optional[str] = None,
        status: Optional[Literal["active", "disabled"]] = None,
    ) -> Dict[str, Any]:
        """Update a memory function.

        Args:
            memory_function_id (ID_T): The memory function's ID.
            name (Optional[str], optional): The memory function's name. Defaults to None.
            schema (Optional[Union[BaseModel, dict]], optional): The memory function's schema. Defaults to None.
            custom_instructions (Optional[str], optional): The memory function's custom instructions. Defaults to None.
            description (Optional[str], optional): The memory function's description. Defaults to None.
            function_type (Optional[str], optional): The memory function's type. Defaults to None.
            status: Optional[Literal["active", "disabled"]], optional): The memory function's status.
                Use to activate or disable the memory function. Disabled memory functions no longer
                trigger on new threads.

        Returns:
            Dict[str, Any]: The memory function's data.
        """

        data: Dict[str, Any] = {
            "name": name,
            "description": description,
            "custom_instructions": custom_instructions,
            "type": function_type,
            "status": status,
        }
        if schema is not None:
            data["function"] = (
                schema
                if isinstance(schema, dict)
                else json.loads(schema.model_dump_json())
            )
        response = await self.client.patch(
            f"/memory-functions/{_as_uuid(memory_function_id)}",
            json={k: v for k, v in data.items() if v is not None},
        )
        raise_for_status_with_text(response)
        return response.json()

    async def create_thread(
        self,
        *,
        thread_id: Optional[ID_T] = None,
        messages: Optional[Sequence[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create a thread.

        Args:
            thread_id (ID_T): The thread's ID.
            messages (Sequence[Dict[str, Any]]): A sequence of dictionaries representing the messages in the thread.
            metadata (Dict[str, str]): Additional metadata associated with the thread.

        Returns:
            Dict[str, Any]: The thread's data.
        """

        data = {
            "id": thread_id,
            "messages": messages,
            "metadata": metadata,
        }
        response = await self.client.post("/threads", json=data)
        raise_for_status_with_text(response)
        return response.json()

    async def add_messages(
        self, thread_id: ID_T, *, messages: Sequence[schemas.MESSAGE_LIKE]
    ) -> None:
        """Add messages to a thread.

        This method allows you to add messages to a specific thread identified by its ID.

        Args:
            thread_id (ID_T): The ID of the thread to which the messages will be added.
            messages (Sequence[Dict[str, Any]]): A sequence of dictionaries representing the messages to be added. Each dictionary should contain the following keys:
                - "role" (str): The role of the message sender (e.g., "user", "bot").
                - "content" (str): The content of the message.
                - "name" (str): The name of the message sender.
                - "metadata" (dict): Additional metadata associated with the message.

        Returns:
            None

        Examples:
            Add messages in a new thread:

            >>> from langmem import Client
            >>> client = Client()
            >>> messages = [
            ...     {
            ...         "role": "user",
            ...         "content": "Did you know pikas make their own haypiles?",
            ...         "name": "Will",
            ...         "metadata": {"user_id": user_id},
            ...     },
            ...     {
            ...         "role": "assistant",
            ...         "content": "Yes, pikas are fascinating creatures!",
            ...         "name": "Bot",
            ...     },
            ... ]
            >>> await client.add_messages(thread_id, messages=messages)
        """

        data = {"messages": messages}
        response = await self.client.post(
            f"/threads/{_as_uuid(thread_id)}/add_messages",
            data=json.dumps(data, default=_default_serializer),  # type: ignore[arg-type]
        )
        raise_for_status_with_text(response)
        return response.json()

    async def get_thread(self, thread_id: ID_T) -> Dict[str, Any]:
        """Get a thread.

        Args:
            thread_id (ID_T): The thread's ID.

        Returns:
            Dict[str, Any]: The thread's data.
        """

        response = await self.client.get(f"/threads/{_as_uuid(thread_id)}")
        raise_for_status_with_text(response)
        return response.json()

    async def list_threads(self) -> Iterable[Dict[str, Any]]:
        """List threads.

        Returns:
            Iterable[Dict[str, Any]]: The threads' data.
        """

        response = await self.client.get("/threads")
        raise_for_status_with_text(response)
        return response.json()

    async def list_thread_memory(self, thread_id: ID_T) -> List[Dict[str, Any]]:
        """List a thread's memory.

        This method retrieves all memories associated with a given thread.
        It will return outputs from all memory function types defined for the thread.

        Args:
            thread_id (ID_T): The thread's ID.

        Returns:
            List[Dict[str, Any]]: The thread's memory.

        Examples:

            >>> from langmem import AsyncClient
            >>> client = AsyncClient()
            >>> thread_id = "e4d2c7a0-9441-4ea2-8ebe-2204f3e95a28"
            >>> memories = client.list_thread_memory(thread_id)
            >>> async for memory in memories:
            ...     print(memory)
        """

        response = await self.client.get(f"/threads/{_as_uuid(thread_id)}/memory")
        raise_for_status_with_text(response)
        return response.json()

    async def get_thread_memory(
        self,
        thread_id: ID_T,
        *,
        memory_function_id: ID_T,
    ) -> dict:
        """Get a thread's memory state.

        This method retrieves the current memory state for a specific thread and memory function.
        It is faster than querying and useful for "thread_state" type memories.

        Args:
            thread_id (ID_T): The thread's ID.
            memory_function_id (ID_T): The memory function's ID.

        Returns:
            dict: The memory state.

        Examples:

            >>> from langmem import AsyncClient
            >>> client = AsyncClient()
            >>> thread_id = "e4d2c7a0-9441-4ea2-8ebe-2204f3e95a28"
            >>> memory_function_id = "cb217ff7-963e-44fc-b222-01f01058d64b"
            >>> await client.get_thread_memory(thread_id, memory_function_id=memory_function_id)
        """
        response = await self.client.get(
            f"/threads/{_as_uuid(thread_id)}/memory/{_as_uuid(memory_function_id)}/state"
        )
        raise_for_status_with_text(response)
        return response.json()

    async def trigger_all_for_thread(self, thread_id: ID_T) -> None:
        """Trigger all memory functions for a thread.

        This method eagerly processes any pending memories for the given thread.
        It will trigger all memory function types defined for the thread.

        Args:
            thread_id (ID_T): The thread's ID.

        Examples:

            >>> from langmem import Client
            >>> client = Client()
            >>> thread_id = "e4d2c7a0-9441-4ea2-8ebe-2204f3e95a28"
            >>> await client.trigger_all_for_thread(thread_id)
        """

        response = await self.client.post(f"/threads/{_as_uuid(thread_id)}/trigger-all")
        raise_for_status_with_text(response)
        return response.json()

    async def add_thread_state(
        self, thread_id: ID_T, state: Dict[str, Any], *, key: Optional[str] = None
    ) -> None:
        """Add a thread state.

        Args:
            thread_id (ID_T): The thread's ID.
            state (Dict[str, Any]): The thread state.
        """

        response = await self.client.post(
            f"/threads/{_as_uuid(thread_id)}/thread_state",
            json={"state": state, "key": key},
        )
        raise_for_status_with_text(response)
        return response.json()

    async def get_thread_state(
        self, thread_id: ID_T, *, key: Optional[str] = None
    ) -> dict:
        """Get a thread state.

        Args:
            thread_id (ID_T): The thread's ID.

        Returns:
            GetThreadStateResponse: The thread state.
        """
        response = await self.client.post(
            f"/threads/{_as_uuid(thread_id)}/thread_state/query", json={"key": key}
        )
        raise_for_status_with_text(response)
        return response.json()

    async def list_messages(
        self,
        thread_id: ID_T,
        *,
        response_format: Optional[Literal["openai", "langmem"]] = None,
        ascending_order: Optional[bool] = None,
        page_size: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """List a thread's messages.

        Args:
            thread_id (ID_T): The thread's ID.
            response_format (Optional[Literal["openai", "langmem"]], optional): The response format.
                Defaults to None, which is the openai format.
            ascending_order (Optional[bool], optional): Whether to return messages in ascending order.
            page_size (Optional[int], optional): The page size. Defaults to None.
            limit (Optional[int], optional): The maximum number of messages to return. Defaults to None.

        Returns:
            AsyncGenerator[Dict[str, Any], None]: The messages' data.
        """

        params: Dict[str, Any] = {
            "response_format": response_format,
            "page_size": page_size,
            "ascending_order": ascending_order,
        }
        params = {k: v for k, v in params.items() if v is not None}

        # Handle pagination for large threads
        cursor = None
        idx = 0
        while True:
            if cursor is not None:
                params["cursor"] = cursor
            response = await self.client.get(
                f"/threads/{_as_uuid(thread_id)}/messages", params=params
            )
            raise_for_status_with_text(response)
            data = response.json()
            for message in data.get("messages", []):
                yield message
                idx += 1
                if limit is not None and idx >= limit:
                    break
            cursor = data.get("next_cursor")
            if cursor is None or (limit is not None and idx >= limit):
                break


class Client:
    """The Langmem client.

    Examples:

        Basic usage:

            >>> from langmem import Client
            >>> from pydantic import BaseModel, Field
            >>> client = Client()
            >>> class UserProfile(BaseModel):
            ...     name: str = Field(description="The user's name")
            ...     age: int = Field(description="The user's age")
            ...     interests: List[str] = Field(description="The user's interests")
            ...     relationships: Dict[str, str] = Field(
            ...         description="The user's friends, family, pets,and other relationships."
            ...     )
            >>> memory_function = client.create_memory_function(
            ...     UserProfile,
            ...     target_type="user_state",
            ...     name="User Profile",
            ... )
            >>> user_id = uuid.uuid4()
            >>> user_name = "Will"
            >>> messages = [
            ...     {
            ...         "role": "user",
            ...         "content": "Did you know pikas make their own haypiles?",
            ...         "name": "Will",
            ...         "metadata": {"user_id": user_id},
            ...     },
            ...     {
            ...         "role": "assistant",
            ...         "content": "Yes! And did you know they're actually related to rabbits?",
            ...     },
            ...     {
            ...         "role": "user",
            ...         "content": "I did! More people should know this important knowledge.",
            ...         "name": "Will",
            ...         "metadata": {"user_id": user_id},
            ...     },
            ... ]
            >>> thread_id = uuid.uuid4()
            >>> client.add_messages(thread_id, messages)
            >>> client.trigger_all_for_thread(thread_id)
            >>> client.get_user_memory(user_id, memory_function_id=memory_function["id"])
            >>> # Or query the unstructured memory
            >>> client.query_user_memory(user_id, "pikas", k=1)

            Query user memories semantically:

            >>> client.query_user_memory(
            ...     user_id=user_id,
            ...     text="What does the user think about rabbits?",
            ...     memory_function_ids=[belief_function["id"]],
            ...     k=3,
            ... )

            Create a thread summary memory function:

            >>> class ConversationSummary(BaseModel):
            ...     title: str = Field(description="Distinct for the conversation.")
            ...     summary: str = Field(description="High level summary of the interactions.")
            ...     topic: List[str] = Field(
            ...         description="Tags for topics discussed in this conversation."
            ...     )
            >>> thread_summary_function = client.create_memory_function(
            ...     ConversationSummary, target_type="thread_summary"
            ... )

            Fetch thread messages:

            >>> messages = client.list_messages(thread_id=thread_id)
            >>> for message in messages:
            ...     print(message)
    """

    __slots__ = ["api_key", "client"]

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("LANGMEM_API_KEY")
        base_url = _ensure_url(api_url)
        self.client = httpx.Client(
            base_url=base_url,
            headers=Client._get_headers(self.api_key),
            timeout=DEFAULT_TIMEOUT,
        )

    @staticmethod
    def _get_headers(api_key: Optional[str]):
        if not api_key:
            return {}
        return {
            "x-api-key": api_key,
        }

    @property
    def _headers(self):
        return self._get_headers(self.api_key)

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.client.close()

    def create_user(
        self,
        *,
        user_id: ID_T,
        name: str,
        tags: Optional[Sequence[str]] = None,
        metadata: Dict[str, str] = {},
    ) -> Dict[str, Any]:
        """Create a user.

        Args:
            user_id (ID_T): The user's ID.
            name (str): The user's name.
            tags (Optional[Sequence[str]], optional): The user's tags. Defaults to None.
            metadata (Dict[str, str], optional): The user's metadata. Defaults to {}.

        Returns:
            Dict[str, Any]: The user's data.
        """

        data = {
            "id": user_id,
            "name": name,
            "tags": tags,
            "metadata": metadata,
        }
        response = self.client.post("/users", json=data)
        raise_for_status_with_text(response)
        return response.json()

    def get_user(self, user_id: ID_T) -> Dict[str, Any]:
        """Get a user.

        Args:
            user_id (ID_T): The user's ID.

        Returns:
            Dict[str, Any]: The user's data.
        """
        response = self.client.get(f"/users/{_as_uuid(user_id)}")
        raise_for_status_with_text(response)
        return response.json()

    def update_user(
        self,
        user_id: ID_T,
        *,
        name: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Update a user.

        Args:
            user_id (ID_T): The user's ID.
            name (Optional[str], optional): The user's name. Defaults to None.
            tags (Optional[Sequence[str]], optional): The user's tags. Defaults to None.
            metadata (Optional[Dict[str, str]], optional): The user's metadata. Defaults to None.

        Returns:
            Dict[str, Any]: The user's data.
        """
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if tags is not None:
            data["tags"] = tags
        if metadata is not None:
            data["metadata"] = metadata
        response = self.client.patch(f"/users/{_as_uuid(user_id)}", json=data)
        raise_for_status_with_text(response)
        return response.json()

    def list_users(
        self,
        *,
        name: Optional[Sequence[str]] = None,
        id: Optional[Sequence[ID_T]] = None,
    ) -> Iterable[Dict[str, Any]]:
        """List users.

        Args:
            name (Optional[Sequence[str]], optional): The user's name. Defaults to None.
            id (Optional[Sequence[ID_T]], optional): The user's ID. Defaults to None.

        Returns:
            List[Dict[str, Any]]: The users' data.
        """
        body = {
            "name": name,
            "id": id,
        }
        response = self.client.post(
            "/users/query",
            data=json.dumps(  # type: ignore[arg-type]
                body, default=_default_serializer
            ),
            headers={"Content-Type": "application/json"},
        )
        raise_for_status_with_text(response)
        return response.json()["users"]

    def trigger_all_for_user(self, user_id: ID_T) -> None:
        """Trigger all memory functions for a user.

        Args:
            user_id (ID_T): The user's ID.
        """
        response = self.client.post(f"/users/{_as_uuid(user_id)}/trigger-all")
        raise_for_status_with_text(response)
        return response.json()

    def delete_user_memory(
        self,
        *,
        user_id: ID_T,
        memory_function_id: ID_T,
    ) -> None:
        """Delete a user's memory.

        Args:
            user_id (ID_T): The user's ID.
            memory_function_id (ID_T): The memory function's ID. Defaults to None.
        """
        response = self.client.delete(
            f"/users/{_as_uuid(user_id)}/memory/{_as_uuid(memory_function_id)}/state"
        )
        raise_for_status_with_text(response)
        return response.json()

    def update_user_memory(
        self,
        user_id: ID_T,
        *,
        memory_function_id: ID_T,
        state: dict,
    ) -> None:
        """Update a user's memory.

        Args:
            user_id (ID_T): The user's ID.
            memory_function_id (ID_T): The memory function's ID.
            state (dict): The memory state.
        """
        response = self.client.put(
            f"/users/{_as_uuid(user_id)}/memory/{_as_uuid(memory_function_id)}/state",
            data=json.dumps(  # type: ignore[arg-type]
                {"state": state},
                default=_default_serializer,
            ),
        )
        raise_for_status_with_text(response)
        return response.json()

    def get_user_memory(
        self,
        user_id: ID_T,
        *,
        memory_function_id: ID_T,
    ) -> dict:
        """Get a user's memory state.

        This method retrieves the current memory state for a specific user and memory function.
        It is faster than querying and useful for "user_state" type memories.

        Args:
            user_id (ID_T): The user's ID.
            memory_function_id (ID_T): The memory function's ID.

        Returns:
            dict: The memory state.

        Examples:

            >>> from langmem import Client
            >>> client = Client()
            >>> user_id = "2d1a8daf-2319-4e3e-9fd0-6d7981ceb8a6"
            >>> memory_function_id = "cb217ff7-963e-44fc-b222-01f01058d64b"
            >>> client.get_user_memory(user_id, memory_function_id=memory_function_id)
        """
        response = self.client.get(
            f"/users/{_as_uuid(user_id)}/memory/{_as_uuid(memory_function_id)}/state"
        )
        raise_for_status_with_text(response)
        return response.json()

    def query_user_memory(
        self,
        user_id: ID_T,
        text: str,
        k: int = 200,
        memory_function_ids: Optional[Sequence[ID_T]] = None,
        weights: Optional[dict] = None,
        states_to_return: Optional[Sequence[ID_T]] = None,
        thread_summaries: Optional[Sequence[ID_T]] = None,
        thread_summaries_k: Optional[int] = None,
    ) -> List:
        """Query a user's memory.

        Args:
            user_id (ID_T): The user's ID.
            text (str): The query text.
            k (int, optional): The number of results to return. Defaults to 200.
            memory_function_ids (Optional[Sequence[ID_T]], optional): Semantic memory outputs
                to include. Defaults to None, meaning just the unstructured memories.
            weights (Optional[dict], optional): Weights for the different memory types.
                Backend default equally weights relevance, recency, and importance.
                Defaults to None.
            states_to_return (Optional[Sequence[ID_T]], optional): The user state
                memory function IDs to include in the response.

        Returns:
            List: The query results.


        Examples:

            Query a user's semantic memory:
                >>> from langmem import Client
                >>> client = Client()
                >>> user_id = uuid.uuid4()
                >>> client.query_user_memory(user_id, text="pikas", k=10)

            Query the memory, ignoring recency or perceived importance:

                >>> client.query_user_memory(
                ...     user_id,
                ...     text="pikas",
                ...     k=10,
                ...     weights={"relevance": 1.0, "recency": 0.0, "importance": 0.0},
                ... )

            Include user state memories in the response (to save the number of API calls):
                >>> mem_functions = [
                ...     f["id"]
                ...     for f in client.list_memory_functions(target_type="user")
                ...     if f["type"] == "user_state"
                ... ]
                >>> client.query_user_memory(
                ...     user_id,
                ...     text="pikas",
                ...     k=10,
                ...     states_to_return=mem_functions,
                ... )

            Query over user_append_state memories:
                >>> mem_functions = [
                ...    f["id"]
                ...    for f in client.list_memory_functions(target_type="user")
                ...    if f["type"] == "user_append_state"
                ... )
                >>> client.query_user_memory(
                ...     user_id,
                ...     text="pikas",
                ...     k=10,
                ...     memory_function_ids=mem_functions,
                ... )

            Include thread summaries for the most recent threads:

                >>> mem_functions = [
                ...     f["id"] for f in client.list_memory_functions(target_type="thread")
                ... ]
                >>> client.query_user_memory(
                ...     user_id,
                ...     text="pikas",
                ...     k=10,
                ...     thread_summaries=mem_functions,
                ...     thread_summaries_k=5,
                ... )
        """
        thread_query = None
        if thread_summaries is not None:
            thread_query = {
                "memory_function_ids": thread_summaries,
            }
            if thread_summaries_k is not None:
                thread_query["k"] = thread_summaries
        response = self.client.post(
            f"/users/{_as_uuid(user_id)}/memory/query",
            data=json.dumps(  # type: ignore[arg-type]
                {
                    "text": text,
                    "k": k,
                    "memory_function_ids": memory_function_ids,
                    "weights": weights,
                    "state": states_to_return,
                    "thread_query": thread_query,
                },
                default=_default_serializer,
            ),
        )
        raise_for_status_with_text(response)
        return response.json()

    def create_memory_function(
        self,
        parameters: Union[BaseModel, dict],
        *,
        target_type: str = "user_state",
        name: Optional[str] = None,
        description: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        function_id: Optional[ID_T] = None,
    ) -> Dict[str, Any]:
        """Create a memory function.

        Args:
            parameters (Union[BaseModel, dict]): The memory function's parameters.
            target_type (str, optional): The memory function's target type. Defaults to "user_state".
            name (Optional[str], optional): The memory function's name. Defaults to None.
            description (Optional[str], optional): The memory function's description. Defaults to None.
            custom_instructions (Optional[str], optional): The memory function's custom instructions. Defaults to None.
            function_id (Optional[ID_T], optional): The memory function's ID. Defaults to None.

        Returns:
            Dict[str, Any]: The memory function's data.

        Examples:

            Create a user profile memory function:

                >>> from pydantic import BaseModel, Field
                >>> from langmem import Client
                >>> client = Client()
                >>> class UserProfile(BaseModel):
                ...     name: str = Field(description="The user's name")
                ...     age: int = Field(description="The user's age")
                ...     interests: List[str] = Field(description="The user's interests")
                ...     relationships: Dict[str, str] = Field(
                ...         description="The user's friends, family, pets,and other relationships."
                ...     )
                >>> memory_function = client.create_memory_function(
                ...     UserProfile,
                ...     target_type="user_state",
                ...     name="User Profile",
                ... )

            Create an append-only user memory function:

                >>> class FormativeEvent(BaseModel):
                ...     event: str = Field(description="The formative event that occurred.")
                ...     impact: str = Field(description="How this event impacted the user.")
                >>> event_function = client.create_memory_function(
                ...     FormativeEvent, target_type="user_append_state"
                ... )

        """
        if isinstance(parameters, dict):
            params = parameters
        else:
            params = parameters.model_json_schema()
        function_schema = {
            "name": name or params.pop("title", ""),
            "description": description or params.pop("description", ""),
            "parameters": params,
        }
        data = {
            "type": target_type,
            "custom_instructions": custom_instructions,
            "id": function_id or str(uuid.uuid4()),
            "schema": function_schema,
        }
        response = self.client.post("/memory-functions", json=data)
        raise_for_status_with_text(response)
        return response.json()

    def get_memory_function(self, memory_function_id: ID_T) -> Dict[str, Any]:
        """Get a memory function.

        Args:
            memory_function_id (ID_T): The memory function's ID.

        Returns:
            Dict[str, Any]: The memory function's data.
        """
        response = self.client.get(f"/memory-functions/{_as_uuid(memory_function_id)}")
        raise_for_status_with_text(response)
        return response.json()

    def list_memory_functions(
        self, *, target_type: Optional[Sequence[str]] = None
    ) -> Iterable[Dict[str, Any]]:
        """List memory functions.

        Args:
            target_type (Sequence[str], optional): The memory function's target type. Defaults to None.

        Returns:
            List[Dict[str, Any]]: The memory functions' data.
        """
        body = {}
        if target_type is not None:
            body["target_type"] = (
                [target_type] if isinstance(target_type, str) else target_type
            )
        cursor = None
        while True:
            if cursor is not None:
                body["cursor"] = cursor
            response = self.client.post("/memory-functions/query", json=body)
            raise_for_status_with_text(response)
            data = response.json()
            for function in data.get("memory_functions", []):
                yield function
            cursor = data.get("next_cursor")
            if cursor is None:
                break

    def update_memory_function(
        self,
        memory_function_id: ID_T,
        *,
        name: Optional[str] = None,
        schema: Optional[Union[BaseModel, dict]] = None,
        custom_instructions: Optional[str] = None,
        description: Optional[str] = None,
        function_type: Optional[str] = None,
        status: Optional[Literal["active", "disabled"]] = None,
    ) -> Dict[str, Any]:
        """Update a memory function.

        Args:
            memory_function_id (ID_T): The memory function's ID.
            name (Optional[str], optional): The memory function's name. Defaults to None.
            schema (Optional[Union[BaseModel, dict]], optional): The memory function's schema. Defaults to None.
            custom_instructions (Optional[str], optional): The memory function's custom instructions. Defaults to None.
            description (Optional[str], optional): The memory function's description. Defaults to None.
            function_type (Optional[str], optional): The memory function's type. Defaults to None.
            status: Optional[Literal["active", "disabled"]], optional): The memory function's status.
                Use to activate or disable the memory function. Disabled memory functions no longer
                trigger on new threads.

        Returns:
            Dict[str, Any]: The memory function's data.


        Examples:

            Update a memory function's name:
                >>> from langmem import Client
                >>> client = Client()
                >>> memory_function_id = list(client.list_memory_functions())[0]["id"]
                >>> client.update_memory_function(memory_function_id, name="New Name")

            Disable a memory function:
                >>> client.update_memory_function(memory_function_id, status="disabled")

            Update a memory function's schema:
                >>> from pydantic import BaseModel, Field
                >>> class UserProfile:
                ...     name: str = Field(description="The user's name")
                ...     favorite_animals: List[str] = Field(
                ...         description="The user's favorite animals"
                ...     )
                >>> client.update_memory_function(memory_function_id, schema=UserProfile)

            Update the custom instructions for a memory function:

                >>> client.update_memory_function(
                ...     memory_function_id,
                ...     custom_instructions="Update the user profile."
                ...     " Never delete anything in the current one."
                ...     " If you don't know, guess as much as you'd like.",
                ... )


        """
        data: dict = {
            "name": name,
            "description": description,
            "custom_instructions": custom_instructions,
            "type": function_type,
            "status": status,
        }
        if schema is not None:
            if isinstance(schema, dict):
                data["schema"] = schema
            else:
                data["schema"] = schema.model_json_schema()
        response = self.client.patch(
            f"/memory-functions/{_as_uuid(memory_function_id)}",
            json={k: v for k, v in data.items() if v is not None},
        )
        raise_for_status_with_text(response)
        return response.json()

    def delete_memory_function(
        self,
        memory_function_id: ID_T,
    ) -> None:
        """Delete a memory function.

        Args:
            memory_function_id (ID_T): The memory function's ID.
        """
        response = self.client.delete(
            f"/memory-functions/{_as_uuid(memory_function_id)}"
        )
        raise_for_status_with_text(response)
        return response.json()

    def create_thread(
        self,
        *,
        thread_id: Optional[ID_T] = None,
        messages: Optional[Sequence[schemas.MESSAGE_LIKE]] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create a thread.

        Args:
            thread_id (ID_T): The thread's ID.
            messages (Sequence[Dict[str, Any]]): The messages to add.
            metadata (Dict[str, str], optional): The thread's metadata. Defaults to {}.

        Returns:
            Dict[str, Any]: The thread's data.
        """
        data = {
            "id": thread_id,
            "messages": messages,
            "metadata": metadata,
        }
        response = self.client.post("/threads", json=data)
        raise_for_status_with_text(response)
        return response.json()

    def add_messages(
        self, thread_id: ID_T, *, messages: Sequence[Dict[str, Any]]
    ) -> None:
        """Add messages to a thread.

        This method allows you to add multiple messages to a specific thread identified by its ID.
        If the thread is not found, it will be created implicitly.

        Args:
            thread_id (ID_T): The ID of the thread to which the messages will be added.
            messages (Sequence[Dict[str, Any]]): A sequence of dictionaries representing the messages to be added.
                Each dictionary should contain the necessary information for a single message, such as its content,
                author, timestamp, etc.

        Examples:

            Add messages in a new thread:

            >>> from langmem import Client
            >>> client = Client()
            >>> messages = [
            ...     {
            ...         "role": "user",
            ...         "content": "Did you know pikas make their own haypiles?",
            ...         "name": "Will",
            ...         "metadata": {"user_id": user_id},
            ...     },
            ...     {
            ...         "role": "assistant",
            ...         "content": "Yes, pikas are fascinating creatures!",
            ...         "name": "Bot",
            ...     },
            ... ]
            >>> client.add_messages(thread_id, messages=messages)


        Raises:
            HTTPError: If the request to add the messages fails.

        Returns:
            None: This method does not return any value.
        """
        data = {"messages": messages}
        response = self.client.post(
            f"/threads/{_as_uuid(thread_id)}/add_messages",
            data=json.dumps(data, default=_default_serializer),  # type: ignore[arg-type]
        )
        raise_for_status_with_text(response)
        return response.json()

    def get_thread(self, thread_id: ID_T) -> Dict[str, Any]:
        """Get a thread.

        Args:
            thread_id (ID_T): The thread's ID.

        Returns:
            Dict[str, Any]: The thread's data.
        """
        response = self.client.get(f"/threads/{_as_uuid(thread_id)}")
        raise_for_status_with_text(response)
        return response.json()

    def list_threads(self) -> Iterable[Dict[str, Any]]:
        """List threads.

        Returns:
            Iterable[Dict[str, Any]]: The threads' data.
        """
        response = self.client.get("/threads")
        raise_for_status_with_text(response)
        return response.json()

    def list_thread_memory(self, thread_id: ID_T) -> List[Dict[str, Any]]:
        """List a thread's memory.

        This method retrieves all memories associated with a given thread.
        It will return outputs from all memory function types defined for the thread.

        Args:
            thread_id (ID_T): The thread's ID.

        Returns:
            List[Dict[str, Any]]: The thread's memory.

        Examples:

            >>> from langmem import Client
            >>> client = Client()
            >>> thread_id = "e4d2c7a0-9441-4ea2-8ebe-2204f3e95a28"
            >>> memories = client.list_thread_memory(thread_id)
            >>> for memory in memories:
            ...     print(memory)
        """
        response = self.client.get(f"/threads/{_as_uuid(thread_id)}/memory")
        raise_for_status_with_text(response)
        return response.json()

    def trigger_all_for_thread(self, thread_id: ID_T) -> None:
        """Trigger all memory functions for a thread.

        This method eagerly processes any pending memories for the given thread.
        It will trigger all memory function types defined for the thread.

        Args:
            thread_id (ID_T): The thread's ID.

        Examples:

            >>> from langmem import Client
            >>> client = Client()
            >>> thread_id = "e4d2c7a0-9441-4ea2-8ebe-2204f3e95a28"
            >>> client.trigger_all_for_thread(thread_id)
        """
        response = self.client.post(f"/threads/{_as_uuid(thread_id)}/trigger-all")
        raise_for_status_with_text(response)
        return response.json()

    def get_thread_memory(
        self,
        thread_id: ID_T,
        *,
        memory_function_id: ID_T,
    ) -> dict:
        """Get a thread's memory state.

        This method retrieves the current memory state for a specific thread and memory function.
        It is faster than querying and useful for "thread_state" type memories.

        Args:
            thread_id (ID_T): The thread's ID.
            memory_function_id (ID_T): The memory function's ID.

        Returns:
            dict: The memory state.

        Examples:

            >>> from langmem import Client
            >>> client = Client()
            >>> thread_id = "e4d2c7a0-9441-4ea2-8ebe-2204f3e95a28"
            >>> memory_function_id = "cb217ff7-963e-44fc-b222-01f01058d64b"
            >>> client.get_thread_memory(thread_id, memory_function_id=memory_function_id)
        """
        response = self.client.get(
            f"/threads/{_as_uuid(thread_id)}/memory/{_as_uuid(memory_function_id)}/state"
        )
        raise_for_status_with_text(response)
        return response.json()

    def add_thread_state(
        self, thread_id: ID_T, state: Dict[str, Any], *, key: Optional[str] = None
    ) -> None:
        """Add a thread state.

        Args:
            thread_id (ID_T): The thread's ID.
            state (Dict[str, Any]): The thread state.
        """
        response = self.client.post(
            f"/threads/{_as_uuid(thread_id)}/thread_state",
            json={"state": state, "key": key},
        )
        raise_for_status_with_text(response)
        return response.json()

    def get_thread_state(self, thread_id: ID_T, *, key: Optional[str] = None) -> dict:
        """Get a thread state.

        Args:
            thread_id (ID_T): The thread's ID.

        Returns:
            GetThreadStateResponse: The thread state.
        """
        response = self.client.post(
            f"/threads/{_as_uuid(thread_id)}/thread_state/query", json={"key": key}
        )
        raise_for_status_with_text(response)
        return response.json()

    def list_messages(
        self,
        thread_id: ID_T,
        *,
        response_format: Optional[Literal["openai", "langmem"]] = None,
        page_size: Optional[int] = None,
        limit: Optional[int] = None,
        ascending_order: Optional[bool] = None,
    ) -> Iterable[Dict[str, Any]]:
        """List a thread's messages.

        Args:
            thread_id (ID_T): The thread's ID.
            response_format (Optional[Literal["openai", "langmem"]], optional): The response format.
                Defaults to None, which is the openai format.
            page_size (Optional[int], optional): The page size. Defaults to None.
            limit (Optional[int], optional): The maximum number of messages to return. Defaults to None.
            ascending_order (Optional[bool], optional): Whether to return messages in ascending_order order.
                Defaults to None.

        Returns:
            Iterable[Dict[str, Any]]: The messages' data.
        """
        params: Dict[str, Any] = {
            "response_format": response_format,
            "page_size": page_size,
            "ascending_order": ascending_order,
        }
        params = {k: v for k, v in params.items() if v is not None}
        cursor: Optional[str] = None
        idx = 0
        while True:
            if cursor is not None:
                params["cursor"] = cursor
            response = self.client.get(
                f"/threads/{_as_uuid(thread_id)}/messages", params=params
            )
            raise_for_status_with_text(response)
            data = response.json()
            for message in data.get("messages", []):
                yield message
                idx += 1
                if limit is not None and idx >= limit:
                    break
            cursor = data.get("next_cursor")
            if cursor is None or (limit is not None and idx >= limit):
                break
