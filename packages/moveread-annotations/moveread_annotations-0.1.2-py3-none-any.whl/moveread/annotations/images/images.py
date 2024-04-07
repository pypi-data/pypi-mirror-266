from typing import Literal, Any
from pydantic import RootModel, ValidationError, ConfigDict
import haskellian.either as E
from moveread.boxes import Annotations, Rectangle
from moveread.errors import InvalidData, InvalidMeta, InexistentSchema

Source = Literal['raw-scan', 'corrected-scan', 'camera', 'corrected-camera'] 

class ImageMeta(Annotations):
  model_config = ConfigDict(extra='forbid')
  source: Source | None = None

ImageSchemas = dict(
  grid_coords=RootModel[Rectangle],
  source=RootModel[Source]
)

def validate(schema: str, metadata) -> E.Either[InvalidMeta, Any]:
  if not schema in ImageSchemas:
    msg = f"Schema {schema} doesn't exist. Available schemas are {list(ImageSchemas.keys())}"
    return E.Left(InexistentSchema(schema, detail=msg))
  try:
    return E.Right(ImageSchemas[schema].model_validate(metadata).model_dump(exclude_none=True))
  except ValidationError as e:
    return E.Left(InvalidData(str(e)))