from typing import TypeVar, Any
from abc import ABC, abstractmethod
import asyncio
import haskellian.either as E
from kv.api import AsyncAPI

from ..models import Game

T = TypeVar('T')

class CoreAPI(ABC):
  @property
  @abstractmethod
  def games(self) -> AsyncAPI[Game]: ...
  @property
  @abstractmethod
  def blobs(self) -> AsyncAPI[bytes]: ...

  async def rollback(self) -> E.Either[Any, None]:
    eithers = await asyncio.gather(
      self.games.rollback(),
      self.blobs.rollback()
    )
    return E.sequence(eithers) | (lambda _: None)
  
  async def commit(self) -> E.Either[Any, None]:
    eithers = await asyncio.gather(
      self.games.commit(),
      self.blobs.commit()
    )
    return E.sequence(eithers) | (lambda _: None)
  