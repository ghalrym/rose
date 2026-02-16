# Abstract Factory

Provide an interface for creating **families of related or dependent objects** without specifying their concrete classes.

## When to use

- You need to ensure that a set of objects is used together (e.g. UI: buttons + text fields from the same theme; DB: connection + repository for the same backend).
- You want to switch entire families (e.g. “light theme” vs “dark theme”, “PostgreSQL” vs “MongoDB”) without changing client code.

## Structure

- **AbstractFactory**: Declares creation methods for each product in the family.
- **ConcreteFactory**: Implements those methods and returns concrete products.
- **AbstractProduct** (per product type): Interface for one kind of product.
- **ConcreteProduct**: Implementation; belongs to one family.

## Python example: UI theme factory

```python
from abc import ABC, abstractmethod

# --- Abstract products ---
class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

class TextField(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

# --- Concrete products: Light theme ---
class LightButton(Button):
    def render(self) -> str:
        return "<button class='light'>Click</button>"

class LightTextField(TextField):
    def render(self) -> str:
        return "<input class='light' type='text'>"

# --- Concrete products: Dark theme ---
class DarkButton(Button):
    def render(self) -> str:
        return "<button class='dark'>Click</button>"

class DarkTextField(TextField):
    def render(self) -> str:
        return "<input class='dark' type='text'>"

# --- Abstract factory ---
class UIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

    @abstractmethod
    def create_text_field(self) -> TextField:
        pass

# --- Concrete factories ---
class LightUIFactory(UIFactory):
    def create_button(self) -> Button:
        return LightButton()

    def create_text_field(self) -> TextField:
        return LightTextField()

class DarkUIFactory(UIFactory):
    def create_button(self) -> Button:
        return DarkButton()

    def create_text_field(self) -> TextField:
        return DarkTextField()


# --- Client: uses only the abstract factory and products ---
def build_form(factory: UIFactory) -> str:
    button = factory.create_button()
    text_field = factory.create_text_field()
    return f"{text_field.render()}\n{button.render()}"

# Usage
light_form = build_form(LightUIFactory())
dark_form = build_form(DarkUIFactory())
print(light_form)  # Light theme elements
print(dark_form)   # Dark theme elements
```

## Python example: data access factory (SQL vs NoSQL)

```python
from abc import ABC, abstractmethod

class UserRepo(ABC):
    @abstractmethod
    def get(self, user_id: str) -> dict | None:
        pass

    @abstractmethod
    def save(self, user: dict) -> None:
        pass

class Cache(ABC):
    @abstractmethod
    def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    def set(self, key: str, value: str) -> None:
        pass

# --- PostgreSQL family ---
class PostgresUserRepo(UserRepo):
    def __init__(self, conn_string: str):
        self.conn_string = conn_string
    def get(self, user_id: str) -> dict | None:
        return {"id": user_id, "source": "postgres"}
    def save(self, user: dict) -> None:
        pass

class RedisCache(Cache):
    def get(self, key: str) -> str | None:
        return None
    def set(self, key: str, value: str) -> None:
        pass

# --- MongoDB family ---
class MongoUserRepo(UserRepo):
    def __init__(self, conn_string: str):
        self.conn_string = conn_string
    def get(self, user_id: str) -> dict | None:
        return {"id": user_id, "source": "mongo"}
    def save(self, user: dict) -> None:
        pass

class MemcacheCache(Cache):
    def get(self, key: str) -> str | None:
        return None
    def set(self, key: str, value: str) -> None:
        pass

# --- Abstract factory ---
class DataAccessFactory(ABC):
    @abstractmethod
    def create_user_repo(self, conn_string: str) -> UserRepo:
        pass

    @abstractmethod
    def create_cache(self) -> Cache:
        pass

class PostgresDataAccessFactory(DataAccessFactory):
    def create_user_repo(self, conn_string: str) -> UserRepo:
        return PostgresUserRepo(conn_string)
    def create_cache(self) -> Cache:
        return RedisCache()

class MongoDataAccessFactory(DataAccessFactory):
    def create_user_repo(self, conn_string: str) -> UserRepo:
        return MongoUserRepo(conn_string)
    def create_cache(self) -> Cache:
        return MemcacheCache()

# Usage: switch entire stack by choosing factory
def get_user(factory: DataAccessFactory, user_id: str, conn: str) -> dict | None:
    repo = factory.create_user_repo(conn)
    cache = factory.create_cache()
    cached = cache.get(f"user:{user_id}")
    if cached:
        return {"cached": True}
    return repo.get(user_id)
```

## Summary

| Pros | Cons |
|------|------|
| Products from one family are guaranteed compatible | Many classes (factory + products per family) |
| Easy to add new families | |
| Client code independent of concrete families | |

Use when you have **multiple product types** that must be **used together** and you want to swap **whole families** (themes, backends, platforms).
