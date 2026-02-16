# Builder

Separate the construction of a complex object from its representation so the same construction process can create different representations.

## When to use

- Object has many optional parameters and constructing it in one call is unclear or error-prone.
- You want a fluent, readable way to set properties step by step.
- You need to enforce a valid construction order or validate as you build.

## Structure

- **Director** (optional): Orchestrates the builder and knows the construction steps.
- **Builder**: Abstract interface for building the product (e.g. `set_a()`, `set_b()`).
- **ConcreteBuilder**: Implements the builder; holds the product and assembles it.
- **Product**: The complex object being built. Retrieved from the builder when done.

## Python example: query builder (fluent API)

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class Query:
    table: str
    columns: list[str]
    where: list[str]
    order_by: list[str]
    limit: int | None

    def to_sql(self) -> str:
        cols = ", ".join(self.columns) or "*"
        sql = f"SELECT {cols} FROM {self.table}"
        if self.where:
            sql += " WHERE " + " AND ".join(self.where)
        if self.order_by:
            sql += " ORDER BY " + ", ".join(self.order_by)
        if self.limit is not None:
            sql += f" LIMIT {self.limit}"
        return sql


class QueryBuilder:
    """Builder with fluent interface (returns self)."""
    def __init__(self, table: str):
        self._query = Query(
            table=table,
            columns=[],
            where=[],
            order_by=[],
            limit=None,
        )

    def select(self, *columns: str) -> "QueryBuilder":
        self._query.columns = list(columns)
        return self

    def where(self, condition: str) -> "QueryBuilder":
        self._query.where.append(condition)
        return self

    def order_by(self, *clauses: str) -> "QueryBuilder":
        self._query.order_by = list(clauses)
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._query.limit = n
        return self

    def build(self) -> Query:
        return self._query


# Usage
query = (
    QueryBuilder("users")
    .select("id", "name", "email")
    .where("active = true")
    .where("created_at > '2024-01-01'")
    .order_by("name ASC")
    .limit(10)
    .build()
)
print(query.to_sql())
# SELECT id, name, email FROM users WHERE active = true AND created_at > '2024-01-01' ORDER BY name ASC LIMIT 10
```

## Python example: HTTP request builder

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: Any

class RequestBuilder:
    def __init__(self, base_url: str = ""):
        self._method = "GET"
        self._url = base_url
        self._headers: dict[str, str] = {}
        self._body: Any = None

    def get(self, path: str) -> "RequestBuilder":
        self._method = "GET"
        self._url = (self._url or "") + path
        return self

    def post(self, path: str, body: Any = None) -> "RequestBuilder":
        self._method = "POST"
        self._url = (self._url or "") + path
        self._body = body
        return self

    def header(self, key: str, value: str) -> "RequestBuilder":
        self._headers[key] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            method=self._method,
            url=self._url,
            headers=self._headers.copy(),
            body=self._body,
        )

# Usage
req = (
    RequestBuilder("https://api.example.com")
    .post("/users", body={"name": "Alice"})
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token")
    .build()
)
```

## Alternative: dataclass with defaults + helper

When you don’t need a full builder, a dataclass with defaults and a small helper can be enough:

```python
from dataclasses import dataclass

@dataclass
class Config:
    host: str = "localhost"
    port: int = 5432
    ssl: bool = True
    pool_size: int = 10

def build_config(
    host: str = "localhost",
    port: int = 5432,
    *,
    ssl: bool = True,
    pool_size: int = 10,
) -> Config:
    return Config(host=host, port=port, ssl=ssl, pool_size=pool_size)
```

## Summary

| Pros | Cons |
|------|------|
| Clear, readable construction | Extra builder class to maintain |
| Optional parameters without long constructor | |
| Can enforce order or validation per step | |

Use Builder when you have **many optional parameters** or want a **fluent API**; use a **dataclass + factory function** when construction is simple.
