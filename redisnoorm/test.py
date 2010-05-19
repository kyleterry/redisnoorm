import redisnoorm

class Testing(redisnoorm.RedisResourceBase):
    redis_host = 'localhost'
    redis_port = 6381
    resource_name = 'testing'
    resource_set = 'testing:set'
    resource_next_id = 'testing:id'
    resource_search_key = 'tester'
    field_keys = {'title': 'testing:%s:title'
                , 'tester': 'testing:%s:tester'
                , 'something': 'testing:%s:something'
    }
