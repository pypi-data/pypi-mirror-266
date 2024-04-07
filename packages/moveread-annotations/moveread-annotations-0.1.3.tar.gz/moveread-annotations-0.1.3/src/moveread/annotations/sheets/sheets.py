from typing import Any
from pydantic import BaseModel, RootModel, ValidationError, ConfigDict
import haskellian.either as E
from scoresheet_models import ModelID
from moveread.errors import InvalidMeta, InexistentSchema, InvalidData

class SheetMeta(BaseModel):
  model_config = ConfigDict(extra='forbid')
  model: ModelID | None = None

SheetSchemas: dict[str, type[BaseModel]] = dict(
  model=RootModel[ModelID]
)

def validate(schema: str, metadata) -> E.Either[InvalidMeta, Any]:
  if not schema in SheetSchemas:
    msg = f"Schema {schema} doesn't exist. Available schemas are {list(SheetSchemas.keys())}"
    return E.Left(InexistentSchema(schema, detail=msg))
  try:
    return E.Right(SheetSchemas[schema].model_validate(metadata).model_dump(exclude_none=True))
  except ValidationError as e:
    return E.Left(InvalidData(str(e)))