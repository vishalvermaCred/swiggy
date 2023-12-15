import json
from functools import wraps
import time
import aioredis
from aioredis.errors import ConnectionClosedError
import logging

DELIMITER = "~"
DEFAULT_EXPIRE_TIME = 3600


def print_redis_log(**msg):
    key = msg.get("key", "")
    msg["pattern"] = key
    key_attributes = key.split(DELIMITER)
    if len(key_attributes) >= 2:
        msg["env"] = key_attributes[0]
        msg["base"] = key_attributes[1]
        msg["pattern"] = "{env}{DELIMITER}{base}{DELIMITER}<param>".format(
            env=msg["env"], DELIMITER=DELIMITER, base=msg["base"]
        )
    msg["log_type"] = "redis_log"
    extra_params = {
        "json_message": json.dumps(msg),
    }
    RedisCache.logger.info("redis %s", "log", extra=extra_params)


def log_write_operation(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        print_redis_log(
            key=kwargs.get("key") or args[1],
            operation="set",
            expire_time=kwargs.get("expire_time", DEFAULT_EXPIRE_TIME),
        )
        return response

    return wrapper


def log_read_operation(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time_ns()
        response = await func(*args, **kwargs)
        end_time = time.time_ns()
        status = "miss"
        if response:
            status = "hit"
        time_taken = end_time - start_time
        print_redis_log(key=kwargs.get("key") or args[1], operation="get", time_taken=time_taken, status=status)
        return response

    return wrapper


def get_default_logger_():
    extra = {"source": "Redis library"}
    logging.basicConfig(level=logging.INFO, format="%(asctime)s Redis Library: %(message)s")
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)
    return logger


class RedisCache:
    def __init__(self, namespace: str, expire_time: int = DEFAULT_EXPIRE_TIME, **kwargs):
        self._pool = None
        self.namespace = namespace
        self.expire_time = expire_time
        self.retry_count = 0
        self.is_retry_in_progress = False
        self.host = None
        self.port = None
        RedisCache.logger = kwargs.get("logging_handler", None) or get_default_logger_()

    def _generate_custom_key(self, text):
        return self.namespace + DELIMITER + text

    async def connect(self, host: str, port: int, password=None):
        """
        Setup a connection pool.
        :param host: Redis host
        :param port: Redis port
        :param loop: Event loop
        """
        self.host = host
        self.port = port

        self._pool = await aioredis.create_redis((self.host, self.port), password=password)

    def handle_closed_connection(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ConnectionClosedError as exception:
                RedisCache.logger.critical("RedisCache ConnectionClosedError: %s", exception)
                self = args[0]
                await self.retry_connection()
                raise exception

        return wrapper

    @handle_closed_connection
    @log_read_operation
    async def get(self, key: str):
        """
        Gets the value corresponding to a key from cache.
        :param key: Key name
        :return:
        """
        key = self._generate_custom_key(key)
        data = await self._pool.get(key)
        if data:
            return json.loads(data)
        return None

    @handle_closed_connection
    @log_write_operation
    async def set(self, key: str, value, expiry_time=None):
        """
        Set a key in a cache.
        :param key: Key name
        :param value: Value of the corresponding key
        :return:
        """
        if not expiry_time:
            expiry_time = self.expire_time
        key = self._generate_custom_key(key)
        value = json.dumps(value)
        await self._pool.set(key, value, expire=expiry_time)

    @handle_closed_connection
    @log_write_operation
    async def rpush(self, key: str, values):
        """
        takes list name and list as arguments
        """
        key = self._generate_custom_key(key)
        return await self._pool.rpush(key, *values)

    @handle_closed_connection
    @log_write_operation
    async def rpop(self, key: str):
        """
        takes list name as argument
        """
        key = self._generate_custom_key(key)
        return await self._pool.rpop(key)

    @handle_closed_connection
    @log_write_operation
    async def lpush(self, key: str, values):
        """
        takes list name and list as arguments
        """
        key = self._generate_custom_key(key)
        return await self._pool.lpush(key, *values)

    @handle_closed_connection
    @log_write_operation
    async def lpop(self, key: str):
        """
        takes list name as argument
        """
        key = self._generate_custom_key(key)
        return await self._pool.lpop(key)

    @handle_closed_connection
    async def delete(self, pattern: str = None, patterns: list = None):
        """
        Deletes the key matching the given pattern.
        :param pattern: Pattern
        :return:
        """
        if pattern:
            pattern = self._generate_custom_key(pattern)
            for key in await self._pool.keys(pattern):
                await self._pool.delete(key)

        if patterns:
            patterns = list(map(self._generate_custom_key, patterns))
            combinations = []
            for pattern in patterns:
                combinations.extend(await self._pool.keys(pattern))

            if combinations:
                await self._pool.delete(combinations[0], *combinations)

    @handle_closed_connection
    async def delete_without_pattern(self, key: str = None):
        """
        Deletes the key.
        :param key: key
        :return:
        """
        key = self._generate_custom_key(key)
        await self._pool.delete(key)

    @handle_closed_connection
    @log_write_operation
    async def hset(self, key: str, field: str, value):
        key = self._generate_custom_key(key)
        value = json.dumps(value)
        await self._pool.hset(key, field, value)
        await self._pool.expire(key, self.expire_time)

    @handle_closed_connection
    @log_write_operation
    async def hmset_dict(self, key: str, value: dict):
        key = self._generate_custom_key(key)
        await self._pool.hmset_dict(key, value)
        await self._pool.expire(key, self.expire_time)

    @handle_closed_connection
    @log_read_operation
    async def hget(self, key: str, field: str):
        key = self._generate_custom_key(key)
        data = await self._pool.hget(key, field)
        if not data:
            return None
        return json.loads(data)

    @handle_closed_connection
    @log_read_operation
    async def hgetall(self, key: str):
        key = self._generate_custom_key(key)
        data = await self._pool.hgetall(key, encoding="UTF-8")
        if not data:
            return None
        return data

    @handle_closed_connection
    @log_write_operation
    async def expire(self, key: str, expiry_time: int = DEFAULT_EXPIRE_TIME):
        """
        Set a key in a cache.
        :param key: Key name
        :param value: Value of the corresponding key
        :return:
        """
        if not expiry_time:
            expiry_time = self.expire_time
        key = self._generate_custom_key(key)
        await self._pool.expire(key, expiry_time)

    @handle_closed_connection
    @log_read_operation
    async def hexists(self, key: str, field: str):
        key = self._generate_custom_key(key)
        return await self._pool.hexists(key, field)

    @handle_closed_connection
    async def hdel(self, key: str, field: str):
        key = self._generate_custom_key(key)
        await self._pool.hdel(key, field)

    @handle_closed_connection
    @log_write_operation
    async def sadd(self, key: str, member: str, *members):
        """Add one or more members to a set."""
        key = self._generate_custom_key(key)
        return await self._pool.sadd(key, member, *members)

    @handle_closed_connection
    @log_read_operation
    async def scard(self, key: str):
        """Get the number of members in a set."""
        key = self._generate_custom_key(key)
        return await self._pool.scard(key)

    @handle_closed_connection
    @log_read_operation
    async def smemebers(self, key: str):
        """Get all the members in a set."""
        key = self._generate_custom_key(key)
        return await self._pool.smembers(key)

    @handle_closed_connection
    @log_read_operation
    async def sismember(self, key: str, member: str):
        """Determine if a given value is a member of a set."""
        key = self._generate_custom_key(key)
        return await self._pool.sismember(key, member)

    @handle_closed_connection
    @log_read_operation
    async def incr(self, key: str):
        key = self._generate_custom_key(key)
        data = await self._pool.incr(key)
        if not data:
            return None
        return data

    @handle_closed_connection
    @log_write_operation
    async def decrby(self, key: str, value: int):
        """
        Decrement a key in the cache
        :param key: Key name
        :param value: Value by which the key's value should be decremented
        :return updated count of the key:
        """

        key = self._generate_custom_key(key)
        return await self._pool.decrby(key, value)

    @handle_closed_connection
    @log_write_operation
    async def incrby(self, key: str, value: int):
        """
        Increment a key in the cache
        :param key: Key name
        :param value: Value by which the key's value should be incremented
        :return updated count of the key:
        """

        key = self._generate_custom_key(key)
        return await self._pool.incrby(key, value)

    @handle_closed_connection
    @log_write_operation
    async def lrange(self, key: str, start: int, stop: int):
        """
        Increment a key in the cache
        :param key: Key name
        :param value: Value by which the key's value should be incremented
        :return updated count of the key:
        """

        key = self._generate_custom_key(key)
        return await self._pool.lrange(key, start, stop)

    async def close(self):
        """
        Closes the connection pool.
        """
        if self._pool is not None:
            await self._pool.close()

    async def retry_connection(self):
        RedisCache.logger.info("RedisCache._retry_connection")

        if self.is_retry_in_progress:
            return RedisCache.logger.debug(
                "Aborting as retry already in progress. Last retry count: %s",
                self.retry_count,
            )

        self.is_retry_in_progress = True

        self.retry_count += 1
        RedisCache.logger.info("Retry count: %s", self.retry_count)

        try:
            await self.connect(host=self.host, port=self.port)
        finally:
            self.is_retry_in_progress = False
