# Typing

- Use **Pydantic** for:
  - Request/response and config models
  - Validated data structures and DTOs
  - Any structured data that benefits from validation or serialization
- **API/route responses**: Never return raw `dict` or `list[dict]` from FastAPI (or other HTTP) route handlers. Always declare a Pydantic response model (or return an existing Pydantic model / `list[SomeModel]`) and return instances of that type. This keeps responses typed and documented.
- **Always** type:
  - Every function/method **parameter**
  - Every **return** value (use `-> ReturnType`; use `None` when the function returns nothing)
- Rely on Pydantic models and standard type hints (e.g. `list[str]`, `dict[str, int]`) rather than untyped dicts/lists where structure is known. If a dict has known, consistent keys (e.g. id, name, guild_name), use a **Pydantic model**, **TypedDict**, or **NamedTuple** instead of `dict[str, str]` or `list[dict[str, str]]`.
- **Conversions between types (e.g. Pydantic models)**: Implement the conversion as a method on the **source** type (the "from" class), not as a standalone function or a method on the target type. For example, add `MessageRecord.to_langchain_message(self)` (or a class method that converts a list) on `MessageRecord` instead of a module-level `message_records_to_langchain(messages)`.
- **Create / factory methods**: When building an instance of a type from some input (e.g. stream events, API payload), add a **class method** on that type (e.g. `MessageRecord.from_stream_events(content_deltas, tool_call_events, reasoning=...)`) instead of a standalone function like `build_assistant_message_from_stream(...)`. The class being created owns the knowledge of how to construct itself from that input.
