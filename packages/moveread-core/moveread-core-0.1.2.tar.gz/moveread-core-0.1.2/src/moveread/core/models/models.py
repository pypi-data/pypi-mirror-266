from pydantic import BaseModel, ConfigDict

class Box(BaseModel):
  model_config = ConfigDict(extra='forbid')
  url: str
  meta: dict | None = None

class Image(BaseModel):
  model_config = ConfigDict(extra='forbid')
  url: str
  boxes: list[Box] | None = None
  meta: dict | None = None

class Sheet(BaseModel):
  model_config = ConfigDict(extra='forbid')
  images: list[Image]
  meta: dict | None = None

class Player(BaseModel):
  model_config = ConfigDict(extra='forbid')
  sheets: list[Sheet]
  meta: dict | None = None

class Game(BaseModel):
  model_config = ConfigDict(extra='forbid')
  id: str
  players: list[Player]
  meta: dict | None = None
  