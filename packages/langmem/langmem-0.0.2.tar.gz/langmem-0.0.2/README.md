# LangMem Python SDK

LangMem gives your chat bot long-term memory so it can personalize its interactions to each user and environment.

## 1. Install

To install the LangMem Python SDK, run the following command:

```bash
pip install -U langmem
```

Before using LangMem, make sure to set your API URL and API key as environment variables:

```bash
export LANGMEM_API_URL=https://your-instance-url
export LANGMEM_API_KEY=your-api-key
```

## 2. Save Conversations

LangMem automatically extracts memories from conversations in the background. To save a conversation, use the `add_messages` method:

```python
import uuid
from langmem import AsyncClient

client = AsyncClient()
user_id = str(uuid.uuid4())
thread_id = str(uuid.uuid4())

messages = [
    {"role": "user", "content": "Hi, I love playing basketball!", "metadata": {"user_id": user_id}},
    {"role": "assistant", "content": "That's great! Basketball is a fun sport. Do you have a favorite player?"},
    {"role": "user", "content": "Yeah, Steph Curry is amazing!", "metadata": {"user_id": user_id}}
]

await client.add_messages(thread_id=thread_id, messages=messages)
await client.trigger_all_for_thread(thread_id=thread_id)
```

## 3. Remember

To retrieve relevant memories for a user, use the `query_user_memory` method:

```python
async def completion_with_memory(messages, user_id):
    memories = await client.query_user_memory(
        user_id=user_id,
        text=messages[-1]["content"],
    )
    facts = "\n".join([mem["text"] for mem in memories["memories"]])

    system_prompt = {
        "role": "system",
        "content": "Here are some things you know"
         f" about the user:\n\n{facts}"
        }

    return await completion([system_prompt] + messages)

new_messages = [
    {"role": "user", "content": "Do you remember who my favorite basketball player is?", "metadata": {"user_id": user_id}}
]

response = await completion_with_memory(new_messages, user_id=user_id)
print(response.choices[0].message.content)
```

## Concepts

LangMem organizes conversations into threads, where each thread contains a list of messages with content, role, and optional user information. As the app developer, you can configure different memory types based on your needs.

### Memory Types

LangMem supports three types of user memories (exposed as `memory_function`s):

1. **User State**: A structured profile that LangMem maintains for each user.
2. **Semantic Memory**: An unstructured memory that generates knowledge triplets from conversations. It can be queried based on relevance, importance, and recency.
3. **Append-only State**: A hybrid of the above two memory types that allows you to customize the memory schema while still retrieving based on relevance and recency.

You can also track thread-level memories using the `thread_summary` memory type, which is useful for including summaries of recent conversations in your system prompt.

For more details on memory types and when to use each one, refer to the Memory Types documentation.

## Reference

- **Client**: Documentation for the `Client` and `AsyncClient` objects in the `client.py` file.

## Note

LangMem is currently in early alpha, so expect improvements and potential breaking changes. Your feedback is important to us!

For a more detailed walkthrough of the core functionality, check out the LangMem Walkthrough Notebook.

## Thanks!

Thanks for your feedback! Email your questions and requests to <mailto:will@langchain.dev>.


<p align="center">
  <img src="https://langchain-ai.github.io/long-term-memory/static/img/memy.png" width="80%" alt="memy">
</p>