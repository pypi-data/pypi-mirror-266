# Moveread Annotations

> Annotation schemas for the Moveread Core

## Usage

```python
from moveread.annotations.players import validate

validate('language', 'CA')
# Right(value='CA')

validate('lang', 'CA')
# Left(value=InexistentSchema(schema='lang', detail="Schema lang doesn't exist. Available schemas are ['language', 'style', 'end_correct']"))
```