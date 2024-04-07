import os
from argparse import ArgumentParser
from quicktype_ts import pydantic2typescript
from moveread.annotations.games import GameMeta
from moveread.annotations.players import PlayerMeta
from moveread.annotations.sheets import SheetMeta
from moveread.annotations.images import ImageMeta


def main():

  parser = ArgumentParser()
  parser.add_argument('--src-path', required=True)
  args = parser.parse_args()
  base = os.path.join(args.src_path, 'src')

  models = [('games', GameMeta), ('players', PlayerMeta), ('sheets', SheetMeta), ('images', ImageMeta)]

  os.makedirs(base, exist_ok=True)
  for filename, model in models:
    path = os.path.join(base, f'{filename}.ts')
    print(f'Generating {path}...')
    code = pydantic2typescript(model)
    with open(path, 'wb') as f:
      f.write(code)

  # fix Rectangle
  images = os.path.join(base, 'images.ts')
  os.system("sed -i '/^export type Rectangle/,/}/d' " + images) # delete Rectangle
  rect = """
  // hand-generated as quicktype treats `[number, number]` as `any[]`
  export type Rectangle = {
    size: [number, number]
    tl: [number, number]
  }
  """
  with open(images, 'a') as f:
    f.write(rect)

  print('Successfully generated code!')