from typing import Iterable
import os
from haskellian.either import Either, Left, Right, safe

def ensure_path(file: str):
  dir = os.path.dirname(file)
  if dir != '':
    os.makedirs(dir, exist_ok=True)

def insert(path: str, data: str|bytes, *, exists_ok: bool = False) -> Either[FileExistsError | OSError, None]:
  access = 'w' if exists_ok else 'x'
  mode = f'{access}b' if isinstance(data, bytes) else access
  try:
    ensure_path(path)
    with open(path, mode) as f:
      f.write(data)
      return Right()
  except (FileExistsError, OSError) as e:
    return Left(e)

def update(path: str, data: str|bytes) -> Either[FileNotFoundError | OSError, None]:
  mode = 'r+b' if isinstance(data, bytes) else 'r+'
  try:
    with open(path, mode) as f:
      f.write(data)
      return Right()
  except (FileNotFoundError, OSError) as e:
    return Left(e)

def read(path: str) -> Either[FileNotFoundError | OSError, bytes]:
  try:
    with open(path, 'rb') as f:
      return Right(f.read())
  except (FileNotFoundError, OSError) as e:
    return Left(e)
      
def delete(path: str) -> Either[FileNotFoundError | OSError, None]:
  try:
    os.remove(path)
    safe(lambda: os.removedirs(os.path.dirname(path)))
    return Right(None)
  except (FileNotFoundError, OSError) as e:
    return Left(e)
  
def filenames(base_path: str) -> Iterable[Either[OSError, str]]:
  try:
    for root, _, files in os.walk(base_path):
      for file in files:
        path = os.path.join(root, file)
        yield Right(os.path.relpath(path, start=base_path))
  except OSError as e:
    yield Left(e)

def files(base_path: str) -> Iterable[Either[OSError, tuple[str, bytes]]]:
  try:
    for either in filenames(base_path):
      match either:
        case Right(file):
          with open(os.path.join(base_path, file), 'rb') as f:
            yield Right((file, f.read()))
        case left:
          yield left # type: ignore (poor mypy don't know much about unions)
  except OSError as e:
    yield Left(e)
