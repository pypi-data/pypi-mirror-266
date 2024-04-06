from typing import TypeVar, Generic, Callable, Iterable
from dataclasses import dataclass
import os
from haskellian.either import Either, Left, Right
from kv.api.errors import InexistentItem, InvalidData, ExistentItem, DBError
from ramda import curry
from kv.api import API
from .. import ops

T = TypeVar('T')

@dataclass
class FilesystemKV(API, Generic[T]):

  base_path: str
  extension: str = '.txt'
  parse: Callable[[bytes], Either[InvalidData, T]] = lambda x: Right(x) # type: ignore
  dump: Callable[[T], bytes|str] = lambda x: x # type: ignore

  def _path(self, key: str) -> str:
    return os.path.abspath(os.path.join(self.base_path, f'{key}{self.extension}'))
  
  @curry
  def _parse_err(self, err: OSError, key: str) -> DBError | ExistentItem | InexistentItem:
    match err:
      case FileExistsError():
        return ExistentItem(key, detail=f"File already exists: {self._path(key)}")
      case FileNotFoundError():
        return InexistentItem(key, detail=f"File not found: {self._path(key)}")
      case OSError():
        return DBError(str(err))
  
  def insert(self, key: str, value: T, *, replace: bool = False) -> Either[ExistentItem|DBError, None]:
    return ops.insert(self._path(key), self.dump(value), exists_ok=replace) \
      .mapl(self._parse_err(key=key)) # type: ignore
  
  def update(self, key: str, value: T) -> Either[DBError | InexistentItem, None]:
    return ops.update(self._path(key), self.dump(value)) \
      .mapl(self._parse_err(key=key)) # type: ignore

  def read(self, key: str) -> Either[DBError | InvalidData | InexistentItem, T]:
    either = ops.read(self._path(key)) \
      .mapl(self._parse_err(key=key)) # type: ignore
    return either & self.parse
  
  def delete(self, key: str) -> Either[DBError | InexistentItem, None]:
    return ops.delete(self._path(key)) \
      .mapl(self._parse_err(key=key)) # type: ignore
  
  def keys(self, batch_size: int | None = None) -> Iterable[Either[DBError, str]]:
    for either in ops.filenames(self.base_path):
      yield either.mapl(lambda err: DBError(str(err)))
  
  def items(self, batch_size: int | None = None) -> Iterable[Either[DBError | InvalidData, tuple[str, T]]]:
    for either in ops.files(self.base_path):
      yield either \
      .mapl(lambda err: DBError(str(err))) \
      .bind(lambda entry: self.parse(entry[1]) | (lambda value: (os.path.splitext(entry[0])[0], value)))
  
  def commit(self) -> Either[DBError, None]:
    return Right(None)
  
  def rollback(self) -> Either[DBError, None]:
    return Left(DBError('Rollback not implemented in filesystem API'))
  