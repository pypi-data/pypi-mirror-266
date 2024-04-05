import redis.asyncio as redis_async
import redis


class RedisConnector:
    redis_client_async = None
    redis_client = None

    def __init__(
        self, host: str, password: str = None, decode_responses: bool = False
    ) -> None:
        self._host = host
        assert type(host) is str
        "host must be a str containing redis app name"
        self._password = password
        self._decode_responses = decode_responses

    def connect(self, async_client: bool = False):
        while True:
            try:
                if not async_client:
                    self.redis_client = redis.Redis(
                        host=self._host,
                        port=6379,
                        password=self._password,
                        decode_responses=self._decode_responses,
                    )
                else:
                    self.redis_client_async = redis_async.Redis(
                        host=self._host,
                        port=6379,
                        password=self._password,
                        decode_responses=self._decode_responses,
                    )
                print(f"Connected to Redis: {self._host}")
                break
            except (redis.ConnectionError,) as e:
                print(f"Redis connection error: {e}")
                print(f"retrying to connect...")

    def get_redis_client(self):
        if self.redis_client is None:
            self.connect()
        return self.redis_client

    def get_redis_client_async(self):
        if self.redis_client_async is None:
            self.connect(async_client=True)
        return self.redis_client_async


def get_redis_access(
    app_name: str,
    password: str,
    decode_responses: bool = False,
    restart: bool = False,
    async_client=False,
):
    global _redis_access
    global _redis_access_async

    def init_access(async_client=False):
        global _redis_access
        global _redis_access_async

        _redis_access = None
        _redis_access_async = None

        if not async_client:
            _redis_access = RedisConnector(
                host=app_name, password=password, decode_responses=decode_responses
            )
        else:
            _redis_access_async = RedisConnector(
                host=app_name, password=password, decode_responses=decode_responses
            )

    try:
        if not async_client:
            if not isinstance(_redis_access, RedisConnector) or restart:
                init_access()
        else:
            if not isinstance(_redis_access_async, RedisConnector) or restart:
                init_access(True)
    except NameError:
        if not async_client:
            init_access()
        else:
            init_access(True)
        pass
    return _redis_access if not async_client else _redis_access_async
