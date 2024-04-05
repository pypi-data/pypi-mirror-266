import pymssql
from . import exceptions
import sqlalchemy
import mariadb


class Database:

    def __init__(
            self,
            server: str,
            user: str,
            password: str,
            database: str = None,
            as_dict: bool = True,
            port: int = 1333,
            pool_size: int | sqlalchemy.pool.NullPool = 5,
            max_overflow: int = 10):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.as_dict = as_dict
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self._connection = None
        self._cursor = None
        self._pool = None
        if self.pool_size == sqlalchemy.pool.NullPool:
            pass
        else:
            if self.pool_size < 1:
                raise exceptions.PoolSizeMinException
            if self.max_overflow < self.pool_size:
                raise exceptions.MaxOverflowSizeException

    def __enter__(self):
        self.connect()
        self.get_cursor()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close_connection()

    def get_connection(self):
        pass

    def connect(self):
        self._connection = self._pool.connect()

    @property
    def connection(self):
        return self._connection

    @property
    def connected(self) -> bool:
        try:
            conn = self._pool.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT 1 AS test')
            return True
        except Exception:
            return False

    @property
    def cursor(self):
        return self._cursor

    def get_cursor(self):
        if self._connection is None:
            raise exceptions.ConnectionException
        if self._cursor is None:
            self._cursor = self.connection.cursor()

    def create_pool(self):
        if self._pool is None:
            self._pool = sqlalchemy.pool.QueuePool(
                self.get_connection,
                max_overflow=10,
                pool_size=5)

    @property
    def pool(self):
        return self._pool

    def select(self, query: str, vals: tuple = ()):
        if self._cursor is None:
            raise exceptions.CursorException
        try:
            self._cursor.execute(query, vals)
        except Exception as e:
            return e
        else:
            res = self.fetchall()
            return res
        finally:
            self.close_connection()

    def insert(self, query: str, data: tuple | list[tuple] = ()) -> int:
        if self._cursor is None:
            raise exceptions.CursorException
        try:
            if isinstance(data, tuple):
                self._cursor.execute(query, data)
            else:
                self._cursor.executemany(query, data)
            self._connection.commit()
        except Exception as e:
            return e
        else:
            return self._cursor.rowcount
        finally:
            self.close_connection()

    def fetchall(self):
        try:
            res = self._cursor.fetchall()
        except Exception as e:
            return e
        else:
            return res

    def close_connection(self):
        self._connection.close()


class MsSQLDatabase(Database):

    def __init__(
            self,
            server: str,
            user: str,
            password: str,
            database: str = None,
            as_dict: bool = True,
            port: int = 1433,
            pool_size: int | sqlalchemy.pool.NullPool = 5,
            max_overflow: int = 10) -> pymssql.Connection:
        super().__init__(
            server,
            user,
            password,
            database,
            as_dict,
            pool_size,
            max_overflow)
        self.create_pool()

    def get_connection(self):
        c = pymssql.connect(
            server=self.server,
            user=self.user,
            password=self.password,
            database=self.database,
            as_dict=self.as_dict,
            login_timeout=20,
            timeout=20
        )
        return c

    def get_cursor(self):
        if self._connection is None:
            raise exceptions.ConnectionException
        if self._cursor is None:
            self._cursor = self.connection.cursor()


class MariaDatabase(Database):
    def __init__(
            self,
            server: str,
            user: str,
            password: str,
            database: str = None,
            as_dict: bool = True,
            port: int = 3306,
            pool_size: int | sqlalchemy.pool.NullPool = 5,
            max_overflow: int = 10):
        super().__init__(
            server,
            user,
            password,
            database,
            as_dict,
            port,
            pool_size,
            max_overflow)
        self.create_pool()

    def get_connection(self):
        c = mariadb.connect(
            user=self.user,
            password=self.password,
            host=self.server,
            port=self.port,
            database=self.database
        )
        return c

    def get_cursor(self):
        if self._connection is None:
            raise exceptions.ConnectionException
        if self._cursor is None:
            self._cursor = self._connection.cursor()
        else:
            return self._cursor

    def fetchall(self):
        try:
            res = self._cursor.fetchall()
            if not self.as_dict:
                return res
            else:
                columns = [a[0] for a in self._cursor.description]
                results = [{c: v for c, v in zip(columns, r)} for r in res]
                return results
        except Exception as e:
            return e


if __name__ == '__main__':
    print("""This package is not meant to run as a main file.
          If needed to test, use the pytest set in this package.""")
