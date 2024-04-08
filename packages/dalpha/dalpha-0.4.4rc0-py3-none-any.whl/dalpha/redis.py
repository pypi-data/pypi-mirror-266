import json
import os
from dalpha import get_env_var_or_raise
from dalpha.logging import logger

class DalphaRedisClient:
    def __init__(self, service_code: str, db_num: int = 0):
        self.rd = self.setup(db_num)
        self.namespace = service_code
        
    def __to_redis_key(self, key: str):
        return f"{self.namespace}:{key}"

    def setup(self, db_num):
        try:
            import redis.asyncio as redis
            from redis.backoff import ExponentialBackoff
            from redis.retry import Retry
            from redis.exceptions import (
            BusyLoadingError,
            ConnectionError,
            TimeoutError
            )
            retry = Retry(ExponentialBackoff(), 3)

        except ImportError:
            raise ImportError("Please install redis-py package -> pip install redis")
        
        redis_host = get_env_var_or_raise("REDIS_HOST")
        redis_password = get_env_var_or_raise("REDIS_PASSWORD")
        
        # Optionally, retrieve the REDIS_PORT with a default value if not set
        redis_port = int(os.environ.get("REDIS_PORT") or 6379)

        return redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            password=redis_password,
            retry = retry,
            retry_on_error = [BusyLoadingError, ConnectionError, TimeoutError],
            db = db_num
        )
    
    async def close(self):
        if self.rd:
            await self.rd.close()

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def get(self, key: str):
        redis_key = self.__to_redis_key(key)
        try:
            json_dict = await self.rd.get(redis_key)
            if json_dict:
                return json.loads(json_dict)
            else:
                return None
        except Exception as e:
            logger.error(f"Dalpha Redis Error: {e}")
            return None

    async def set(self, key: str, value, expire: int = None) -> bool:
        redis_key = self.__to_redis_key(key)
        try:
            json_dict = json.dumps(value, ensure_ascii=False).encode("utf-8")
            await self.rd.set(redis_key, json_dict, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Dalpha Redis Error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        redis_key = self.__to_redis_key(key)
        try:
            await self.rd.delete(redis_key)
            return True
        except Exception as e:
            logger.error(f"Dalpha Redis Error: {e}")
            return False

    async def hget(self, key: str, field: str):
        try:
            return await self.rd.hget(self.__to_redis_key(key), field)
        except Exception as e:
            logger.error(f"Dalpha Redis Error: {e}")
            return None
        
    async def hset(self, key: str, map: dict):
        redis_key = self.__to_redis_key(key)
        try:
            await self.rd.hset(redis_key, mapping=map)
        except Exception as e:
            logger.error(f"Dalpha Redis Error: {e}")
            return False
    
    async def hdel(self, key: str, field: str):
        try:
            return await self.rd.hdel(self.__to_redis_key(key), field)
        except Exception as e:
            logger.error(f"Dalpha Redis Error: {e}")
            return None

    async def hkeys(self, key: str, pattern: str="*", batch_count: int=500):
        """
        Retrieve all field names (keys) from a hash matching a pattern with pagination via hscan.

        This method incrementally retrieves keys from a specified hash that match a given pattern,
        doing so in batches to efficiently handle large hashes without loading all fields into memory at once.

        :param key: The key of the hash from which to retrieve field names.
        :param pattern: The pattern to match against the field names, with '*' as a wildcard.
                        This pattern directly applies to the fields in the hash and is not prefixed.
        :param batch_count: The number of fields to attempt to retrieve in each hscan iteration.
        :return: A list of field names (keys) from the hash that match the pattern.
        """
        try:
            cursor = '0'
            fields = []
            full_key = self.__to_redis_key(key)
            while cursor != 0:
                cursor, part_fields = await self.rd.hscan(full_key, cursor, match=pattern, count=batch_count)
                fields.extend(part_fields.keys())
            return fields
        except Exception as e:
            logger.error(f"Dalpha Redis Error: {e}")
            return None

    async def hgetall(self, key: str, pattern = "*", batch_count: int = 500):
        """
        Retrieve all fields and values from a hash with pagination via hscan.
        
        :param key: The hash key.
        :param pattern: The pattern to match against the field names, with '*' as a wildcard.
                        This pattern directly applies to the fields in the hash and is not prefixed.
        :param batch_count: The number of fields to attempt to retrieve in each hscan iteration.
        :return: A dictionary of field names and their corresponding values from the hash that match the pattern.
        """
        try:
            cursor = '0'
            hash_contents = {}
            full_key = self.__to_redis_key(key)
            while cursor != 0:
                cursor, part_data = await self.rd.hscan(full_key, cursor, match=pattern, count=batch_count)
                hash_contents.update(part_data.items())
            return hash_contents
        except Exception as e:
            logger.error(f"Dalpha Redis Error: {e}")
            return None