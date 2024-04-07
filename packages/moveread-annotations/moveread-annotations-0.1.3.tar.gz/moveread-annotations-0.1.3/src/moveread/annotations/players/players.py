from typing import Any
from pydantic import ValidationError, ConfigDict
import haskellian.either as E
from moveread.labels import Annotations, AnnotationSchemas
from moveread.errors import InexistentSchema, InvalidData, InvalidMeta

class PlayerMeta(Annotations):
  model_config = ConfigDict(extra='forbid')

PlayerSchemas = AnnotationSchemas

def validate(schema: str, metadata) -> E.Either[InvalidMeta, Any]:
  if not schema in PlayerSchemas:
    msg = f"Schema {schema} doesn't exist. Available schemas are {list(PlayerSchemas.keys())}"
    return E.Left(InexistentSchema(schema, detail=msg))
  try:
    return E.Right(PlayerSchemas[schema].model_validate(metadata).model_dump(exclude_none=True))
  except ValidationError as e:
    return E.Left(InvalidData(str(e)))