# Sqlite Kv

> Async Key-Value interface over SQLite. Supports any datatype, including JSON and BLOB

## Usage

> Simplest is to use the `SQKliteKV` api

- JSON documents

  ```python
  from sqlite_kv import SQLiteKV

  api = await SQLiteKV.documents(db_path='mydb.sqlite', table='myjsons')
  # or, if you're sure the DB file already exists
  api = SQLiteKV.documents(db_path='mydb.sqlite', table='myjsons', create=False)
  await api.upsert('my-doc', dict(hello='world'))
  await api.read('my-doc') # dict(hello='world')
  ```

- BLOBs
  
  ```python
  from sqlite_kv import SQLiteKV

  api = await SQLiteKV.blobs(db_path='mydb.sqlite', table='myblobs')
  await api.upsert('my-image', b'<super big image>')
  await api.read('my-image') # b'...'
  ```

- Any custom datatype (e.g. JSON, but manually)

  ```python
  import json
  from sqlite_kv import SQLiteKV

  api = await SQLiteKV.new(
    db_path='mydb.sqlite', table='my-jsons',
    dtype='JSON', parse=json.loads, dump=json.dumps
  )
  await api.upsert('my-image', dict(hello='world'))
  await api.read('my-image') # dict(hello='world')
  ```