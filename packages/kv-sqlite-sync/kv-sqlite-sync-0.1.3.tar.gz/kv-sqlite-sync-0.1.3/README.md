# Sqlite Kv (Sync)

> Synchronous Key-Value interface over SQLite. Supports any datatype, including JSON and BLOB

## Usage

```python
import json
from sqlite_kv import SQLiteKV

api = await SQLiteKV.at(
  db_path='mydb.sqlite', table='my-jsons',
  dtype='JSON', parse=json.loads, dump=json.dumps
)
await api.upsert('my-image', dict(hello='world'))
await api.read('my-image') # dict(hello='world')
```