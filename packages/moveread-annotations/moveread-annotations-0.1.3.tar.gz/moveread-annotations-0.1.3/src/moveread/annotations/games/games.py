from typing import Any
from pydantic import BaseModel, RootModel, ConfigDict, ValidationError
import haskellian.either as E
from moveread.errors import InvalidMeta, InvalidData, InexistentSchema, MissingMeta

class Tournament(BaseModel):
  model_config = ConfigDict(extra='forbid')
  name: str | None = None
  group: str | None = None
  round: int | None = None
  board: int | None = None

class Headers(BaseModel):
  model_config = ConfigDict(extra='forbid')
  event: str | None = None
  site: str | None = None
  date: str | None = None
  round: int | None = None
  white: str | None = None
  black: str | None = None
  result: str | None = None

class GameMeta(BaseModel):
  model_config = ConfigDict(extra='forbid')
  tournament: Tournament | None = None
  headers: Headers | None = None
  pgn: str | None = None

GameSchemas = dict(
  tournament=Tournament,
  headers=Headers,
  pgn=RootModel[str]
)

def parse_pgn(meta: dict | None) -> E.Either[MissingMeta|InvalidData, list[str]]:
  if not meta or not 'pgn' in meta:
    return E.Left(MissingMeta('No PGN annotation'))
  elif not isinstance(meta['pgn'], str):
    return E.Left(InvalidData(f'Expected PGN to be `str`, but is {type(meta["pgn"])}'))
  else:
    return E.Right(meta['pgn'].split(' '))

def validate(schema: str, metadata) -> E.Either[InvalidMeta, Any]:
  if not schema in GameSchemas:
    msg = f"Schema {schema} doesn't exist. Available schemas are {list(GameSchemas.keys())}"
    return E.Left(InexistentSchema(schema, detail=msg))
  try:
    return E.Right(GameSchemas[schema].model_validate(metadata).model_dump(exclude_none=True))
  except ValidationError as e:
    return E.Left(InvalidData(str(e)))