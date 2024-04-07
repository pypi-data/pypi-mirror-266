from dataclasses import dataclass, asdict

@dataclass
class GameID:
  gameId: str

  def playerId(self, player: int = 0) -> 'PlayerID':
    return PlayerID(**asdict(self), player=player)

@dataclass
class PlayerID(GameID):
  player: int

  def sheetId(self, page: int = 0) -> 'SheetID':
    return SheetID(**asdict(self), page=page)

@dataclass
class SheetID(PlayerID):
  page: int

  def imageId(self, version: int = 0) -> 'ImageID':
    return ImageID(**asdict(self), version=version)

@dataclass
class ImageID(SheetID):
  version: int = 0

  def boxId(self, idx: int) -> 'BoxID':
    return BoxID(**asdict(self), idx=idx)

@dataclass
class BoxID(SheetID):
  idx: int

ID = GameID | PlayerID | SheetID | ImageID | BoxID