import os
from argparse import ArgumentParser
from quicktype_ts import pydantic2typescript
from moveread.core import Game

def main():

  parser = ArgumentParser()
  parser.add_argument('--src-path', required=True)
  args = parser.parse_args()
  base = os.path.join(args.src_path, 'src')

  os.makedirs(base, exist_ok=True)
  code = pydantic2typescript(Game)

  models = os.path.join(base, 'models.ts')
  print(f'Writing {models}...')
  with open(models, 'wb') as f:
    f.write(code)

  index = os.path.join(base, 'index.ts')
  print(f'Writing {index}...')
  with open(index, 'w') as f:
    f.write("export * from './models.js'\n")

  print('Generated code successfully!')