from typing import Iterable, TypeVar, Generic, Callable, Never, cast
from dataclasses import dataclass
from haskellian.either import Either, Left, Right
from kv.api import API
from kv.api.errors import InexistentItem, DBError, InvalidData
import sqlite3
from .. import queries

T = TypeVar('T')

@dataclass
class SQLiteKV(API[T], Generic[T]):

  conn: sqlite3.Connection
  table: str = 'kv'
  parse: Callable[[str], Either[InvalidData, T]] = lambda x: Right(cast(T, x)) # type: ignore
  dump: Callable[[T], str] = lambda x: str(x)
  dtype: str = 'TEXT'

  @classmethod
  def at(
    cls, db_path: str, table: str = 'kv',
    parse: Callable[[str], Either[InvalidData, T]] = lambda x: Right(cast(T, x)),
    dump: Callable[[T], str] = lambda x: str(x),
    dtype: str = 'TEXT'
  ) -> 'SQLiteKV[T]':
    return SQLiteKV(sqlite3.connect(db_path), table, parse, dump, dtype)

  def __post_init__(self):
    self.conn.execute(*queries.create(self.table, self.dtype))

  def execute(self, query: queries.Query) -> Either[DBError, sqlite3.Cursor]:
    """Safely execute `query` on `self.conn`"""
    try:
      cur = self.conn.execute(*query)
      self.conn.commit()
      return Right(cur)
    except sqlite3.Error as err:
      return Left(DBError(str(err)))

  def update(self, key: str, value: T) -> Either[DBError | InexistentItem, None]:
    return self.execute(queries.update(key, self.dump(value), table=self.table)) \
      & (lambda cur: Left(InexistentItem(key)) if cur.rowcount == 0 else Right())
  
  def insert(self, key: str, value: T, *, replace = False) -> Either[DBError, None]:
    make_query = queries.upsert if replace else queries.insert
    return self.execute(make_query(key, self.dump(value), table=self.table)) | (lambda _: None)
  
  def read(self, key: str) -> Either[DBError | InvalidData | InexistentItem, T]:
    res = self.execute(queries.read(key, table=self.table)) \
      | sqlite3.Cursor.fetchone
    match res:
      case Right(None):
        return Left(InexistentItem(key))
      case Right([data]):
        return self.parse(data)
      case Right(bad_data):
        return Left(InvalidData(detail=f'Found invalid row: {bad_data}'))
      case err:
        return err

  def delete(self, key: str) -> Either[DBError | InexistentItem, None]:
    return self.execute(queries.delete(key, table=self.table)) \
      & (lambda cur: Left(InexistentItem(key)) if cur.rowcount == 0 else Right())
  
  def keys(self, batch_size: int | None = None) -> Iterable[Either[DBError, str]]:
    match self.execute(queries.keys(self.table)):
      case Right(cur):
        while (batch := cur.fetchmany(batch_size or 256)) != []:
          for [key] in batch:
            yield Right(key)
      case Left(err):
        yield Left(err)

  def items(self, batch_size: int | None = None) -> Iterable[Either[DBError | InvalidData, tuple[str, T]]]:
    match self.execute(queries.items(self.table)):
      case Right(cur):
        while (batch := cur.fetchmany(batch_size or 256)) != []:
          for k, v in batch:
            yield self.parse(v) | (lambda v: (k, v))
      case Left(err):
        yield Left(err)
  
  def commit(self) -> Either[Never, None]:
    return Right(self.conn.commit())
  
  def rollback(self) -> Either[Never, None]:
    return Right(self.conn.rollback())