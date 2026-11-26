from typing import Protocol, TypeVar
from ..scheme import BaseModel
from dataclasses import dataclass
# app/
#   domain/
#     user.py              # User, NewUser, UserPatch, errors
#     repositories.py      # Reader, Creator, Updater, Deleter, UserRepository
#   repositories/
#     sqlite/
#       schema.sql
#       user.py            # SqliteUserRepository
#   db/factory.py
#   services/user_service.py
# tests/contract/test_user_repository.py

T = TypeVar("T")            # domain entity (User)
CreateT = TypeVar("CreateT")  # NewUser
PatchT = TypeVar("PatchT")    # UserPatch

@dataclass(frozen=True, slots=True)
class NewUser:
    email: str
    full_name: str
    password_hash: str

@dataclass(frozen=True, slots=True)
class UserPatch:
    email: str | None = None
    full_name: str | None = None

class Reader[T](Protocol):
    async def get(self, id: int) -> T | None: ...

class Creator[T, CreateT](Protocol):
    async def add(self, data: CreateT) -> T: ...

class Updater[T, PatchT](Protocol):
    async def update(self, id: int, patch: PatchT) -> T | None: ...

class Deleter(Protocol):
    async def delete(self, id: int) -> bool: ...


# Entity protocol: compose only what this entity supports, then add domain queries
class UserRepository(
    Reader[User],
    Creator[User, NewUser],
    Updater[User, UserPatch],
    Deleter,
    Protocol,
):
    async def get_by_email(self, email: str) -> User | None: ...
