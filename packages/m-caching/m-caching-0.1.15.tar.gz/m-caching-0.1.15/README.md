# <h2 id="title">LRU Cache</h2>
Thư viện caching của MOBIO. Hỗ trợ cache trên memory hoặc Redis.

#### Cài đặt:
`pip3 install m-caching`

#### Sử dụng:
```
__store_type = StoreType.REDIS # for redis cache
__store_type = StoreType.LOCAL # for memory cache
__file_config = 'config-file-path'

lru_redis_cache = LruCache(store_type=__store_type, config_file_name=__file_config,
                           redis_uri='redis://redis:6379/0',
                           redis_cluster_uri='redis://redis-cluster.redis.svc.cluster.local:6379/0',
                           redis_type=RedisType.REPLICA)

```
Ignore empty values from cache
```
__store_type = StoreType.REDIS
__file_config = 'config-file-path'
lru_cache = LruCache(store_type=__store_type, config_file_name=__file_config)
lru_cache.accept_none(False) # => ignore none values
``` 

#### Usage
cache for class's function
```
class TestCache:
    @lru_cache.add_for_class()
    def test(self, x):
        print("TestCache::test param %s" % x)
        return x + 1

    @staticmethod
    @lru_cache.add()
    def test_static(x):
        print("TestCache::test_static test param %s" % x)
        return x + 1
        
    @staticmethod
    @lru_cache.add_async()
    async def test_static_async(x):
        print("TestCache::test_static test param %s" % x)
        return x + 1
       
    @lru_cache.add_for_class_async()
    async def test_async(self, x):
        print("TestCache::test param %s" % x)
        return x + 1
```

cache for normal function
```
@lru_cache.add()
def some_expensive_method(x):
    print("Calling some_expensive_method(" + str(x) + ")")
    return x + 200
```

#### Example config
```
[REDIS]
host=redis-server
port=6379
cache_prefix=test_cache
```

#### Changedlog:

##### v0.1.14:
- Support Function Async

##### v0.1.13:
- Support RedisCluster

##### v0.1.12:
- Fix bug: missing import;

##### v0.1.11:
- Support python3.9

##### v0.1.10:
- Sửa lại tên version 0.1.9

##### v0.1.9:
- Thêm try...except: khi set item vao redis.