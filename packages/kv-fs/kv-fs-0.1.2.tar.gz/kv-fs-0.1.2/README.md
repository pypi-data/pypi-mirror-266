# Kv Fs

> Simple Key-Value DB implementation on the filesystem

## Usage

- Predefined formats

  ```python
  from kv.fs.json import json_api

  api = json_api('base_path')
  api.insert('greetings/hello', dict(hello='world')) # saves onto 'base_path/greetings/hello.json'
  api.read('greetings/hello') # Right(value=dict(hello='world'))
  ```

- Or build your own:

  ```python
  from kv.fs import FilesystemKV
  from kv.api.errors import InvalidData
  import haskellian.either as E
  import json

  def parse(x: bytes) -> E.Either[InvalidData, Any]:
    try:
      return E.Right(json.loads(x))
    except json.decoder.JSONDecodeError as e:
      return E.Left(InvalidData(e))

  api = FilesystemKV(base_path='data', extension='.json', parse=parse, dump=json.dumps)
  ```