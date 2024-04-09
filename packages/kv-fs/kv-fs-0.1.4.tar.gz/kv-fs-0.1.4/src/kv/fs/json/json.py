import json
from typing import Any
import haskellian.either as E
from kv.api.errors import InvalidData
from ..api import FilesystemKV

def parse(x: bytes) -> E.Either[InvalidData, Any]:
  try:
    return E.Right(json.loads(x))
  except json.decoder.JSONDecodeError as e:
    return E.Left(InvalidData(e))

def dump(x) -> bytes:
  return json.dumps(x).encode()

def json_api(base_path: str) -> FilesystemKV:
  return FilesystemKV(
    base_path, extension='.json', parse=parse, dump=dump
  )