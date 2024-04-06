from typing import Literal, Any
from dataclasses import dataclass

@dataclass(eq=False)
class InexistentItem(BaseException):
  key: str
  detail: Any | None = None
  reason: Literal['inexistent-item'] = 'inexistent-item'

@dataclass(eq=False)
class ExistentItem(BaseException):
  key: str
  detail: Any | None = None
  reason: Literal['existent-item'] = 'existent-item'

@dataclass(eq=False)
class DBError(BaseException):
  detail: Any = None
  reason: Literal['db-error'] = 'db-error'

@dataclass(eq=False)
class InvalidData(BaseException):
  detail: Any = None
  reason: Literal['invalid-data'] = 'invalid-data'