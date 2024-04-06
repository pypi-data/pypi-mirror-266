from typing import TypeVar, AsyncIterable, Generic
from dataclasses import dataclass
from haskellian.either import Either
from ..api import API, AsyncAPI
from ..errors import DBError, ExistentItem, InexistentItem, InvalidData

T = TypeVar('T')

@dataclass
class Asyncify(AsyncAPI[T], Generic[T]):
  """Wrap `api` methods to make them async"""

  api: API[T]

  async def insert(self, key: str, value: T, *, replace: bool = False) -> Either[DBError | ExistentItem, None]:
    return self.api.insert(key, value, replace=replace)

  async def update(self, key: str, value: T) -> Either[DBError | InexistentItem, None]:
    return self.api.update(key, value)

  async def read(self, key: str) -> Either[DBError | InvalidData | InexistentItem, T]:
    return self.api.read(key)

  async def delete(self, key: str) -> Either[DBError | InexistentItem, None]:
    return self.api.delete(key)

  async def keys(self, batch_size: int | None = None) -> AsyncIterable[Either[DBError, str]]:
    for x in self.api.keys(batch_size=batch_size):
      yield x

  async def items(self, batch_size: int | None = None) -> AsyncIterable[Either[DBError | InvalidData, tuple[str, T]]]:
    for x in self.api.items(batch_size=batch_size):
      yield x

  async def commit(self) -> Either[DBError, None]:
    return self.api.commit()

  async def rollback(self) -> Either[DBError, None]:
    return self.api.rollback()