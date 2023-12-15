import asyncpg
from functools import wraps
from logging import getLogger

logger = getLogger(__name__)
LOGGER_KEY = "app.database"

psg_db_instance = None


class Postgres:
    def __init__(self, **kwargs):
        self._pool = None

        self.use_pool = kwargs.get("use_pool", True)
        self.enable_ssl = kwargs.get("enable_ssl", False)
        self.database = kwargs.get("database", None)
        self.user = kwargs.get("user", None)
        self.password = kwargs.get("password", None)
        self.host = kwargs.get("host", None)
        self.port = kwargs.get("port", None)
        self.minsize = kwargs.get("minsize", 10)
        self.maxsize = kwargs.get("maxsize", 100)
        self.keepalives_idle = kwargs.get("keepalives_idle", 5)
        self.keepalives_interval = kwargs.get("keepalives_interval", 4)
        self.max_inactive_connection_lifetime = kwargs.get("max_inactive_connection_lifetime", 90.0)

    async def connect(self):
        """
        Sets connection parameters.
        """
        self._pool = await asyncpg.create_pool(
            user=self.user,
            password=self.password,
            database=self.database,
            host=self.host,
            port=self.port,
            max_inactive_connection_lifetime=self.max_inactive_connection_lifetime,
            min_size=self.minsize,
            max_size=self.maxsize,
        )

    def _establish_connection(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            self = args[0]
            if not self._pool or self._pool._closed:
                await self.connect()
            return await func(*args, **kwargs)

        return wrapper

    @_establish_connection
    async def execute_raw_select_query(self, query) -> list:
        """
        Executes a raw select query.
        Args:
            query: A string indicating the raw SQL statement which will get executed.
        Returns:
            A list of dictionaries with each dictionary represented a row.
        """
        async with self._pool.acquire() as conn:
            try:
                logger.info("raw-select-query:: %s", query)
                result = await conn.fetch(query)
                return list(map(dict, result))
            except Exception as error:
                logger.error(f"Raw Select Query Error:: {query} => {error}")
                raise error

    @_establish_connection
    async def execute_insert_or_update_query(self, query) -> int:
        """
        Executes a raw insert or update statement.
        Args:
            query: A string indicating the raw SQL statement which will get executed.
        Returns:
            An integer
        """
        async with self._pool.acquire() as conn, conn.transaction():
            try:
                logger.debug("insert-or-update-query:: %s", query)
                result = await conn.execute(query)
                return int(float(result.split(" ")[-1]))
            except Exception as error:
                logger.error(f"error in execute_insert_or_update_query:: {query} => {error}")
                raise error

    @_establish_connection
    async def execute_raw_transaction_query(self, query) -> int:
        """
        Executes a raw transaction statement.
        Args:
            query: A string indicating the raw SQL statement which will get executed.
        Returns:
            COMMIT on success and error string on failure
        """
        async with self._pool.acquire() as conn, conn.transaction():
            try:
                result = await conn.execute(query)
                if result != "COMMIT":
                    raise result
                return result
            except Exception as error:
                logger.error(f"Raw Transaction Query Error ::  {query} => {error}")
                raise error

    async def close(self):
        """
        Closes the connection pool.
        """
        logger.info("Closing connection pool")
        await self._pool.close()
