from redis import Redis

class NoOrmError(Exception):
    pass

class NoResourceFoundError(NoOrmError):
    pass

class RedisResourceBase(object):
    """
    Base class for redis "tables."
    Handles basic redis and KV operations.

    This class is to be inherited by a "resource" object.
    """

    redis_host = None
    redis_port = None
    resource_name = None
    resource_next_id = None
    resource_set = None
    resource_search_key = None
    field_set = None

    __valid__ = ['r'
                ,'field_keys'
                ,'id'
    ]

    def __init__(self):
        """
        Init will check to see if self.field_keys exists
        and will start the connection to Redis.
        """
        if not self.redis_host or not self.redis_port:
            raise NoOrmError('You need to define redis_host and redis_port '
                'as class members.')

        if not self.resource_name:
            raise NoOrmError('You need to define resource_name')

        if not self.resource_next_id:
            raise NoOrmError('You need to define resource_next_id')

        if not self.resource_set:
            raise NoOrmError('You need to define resource_set')

        if not self.field_keys:
            raise NoOrmError('Class is missing field_keys dict. Add it!')

        self.r = Redis(
            host=self.redis_host,
            port=int(self.redis_port)
        )

    def __setattr__(self, name, value):
        """
        Used to set the field name as a class property.
        """
        if name not in self.__valid__ and \
           name not in self.field_keys.keys():
            
            raise NoOrmError(
                    '%s is not a valid field for this resource.' % \
                    (name)
            )

        self.__dict__[name] = value

    def __getattr__(self, name):
        """
        Used to get the class property.
        """
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        return False

    def generateId(self):
        """
        Increment and return the next ID in for this resource.
        """
        if not hasattr(self,'resource_next_id'):
            raise NoOrmError('Class is missing resource_next_id property')

        return self.r.incr(self.resource_next_id)

    def load(self, id=None):
        """
        Load a resource.

        TODO: Load a list of resources if no id is passed in.
        """
        if id is None:
            id = self.id

        if id == False:
            raise NoOrmError('Cannot load a resource without an ID!')

        no_resource = True
        for k,v in self.field_keys.iteritems():
            self.__setattr__(k, self.r.get(v % id))

        for k in self.field_keys.keys():
            if getattr(self, k):
                no_resource = False
                break

        if no_resource == True:
            raise NoResourceFoundError(
                    'Resource %s was not found' % str(id)
            )

        self.id = id

        return self

    def save(self):
        """
        Saves a new or updated a current resource. If self.id is set
        it will update the fields for the resource.

        If self.id is NOT set, it will create a new resource.

        TODO: required field and type validation.
        """
        is_new = False
        if not hasattr(self,'id') or self.id == False:
            self.id = self.generateId()
            is_new = True

        keys = self.field_keys.keys()
        for k in keys:
            if getattr(self, k):
                self.r.set(
                    self.field_keys[k] % (str(self.id)),
                    self.__getattr__(k)
                )

        if self.resource_search_key is not None:
            self.setSearchKey(
                getattr(
                    self,
                    self.resource_search_key
                ),
                self.id
            )

        if is_new == True:
            self.addToResourceSet(self.id)

    def destroy(self, id=None):
        """
        This will destroy a resource.

        Bye bye.. all gone.. no more..
        """
        if not id:
            id = self.id

        if id == False:
            raise NoOrmError('Cannot destroy a resource without an ID')
        
        if self.r.sismember(self.resource_set, id):
            for k,v in self.field_keys.iteritems():
                self.r.delete(v % (id))

            if self.resource_search_key:
                self.r.delete(
                    self._build_search_key(
                        getattr(self, self.resource_search_key)
                    )
                )
                
            self.r.srem(self.resource_set, id)
            return True
        return False

    def get(self, key=None):
        """
        Return a value from a key. duh.
        """
        if key is not None:
            return self.r.get(key)
        return False

    def set(self, key=None, value=None):
        """
        Set a value to a key. duh.
        """
        if key is not None:
            return self.r.set(key, value)
        return False

    def addToResourceSet(self, id):
        """
        Adds the newly created resource ID to the collection of IDs.
        """
        return self.r.sadd(self.resource_set, id)
    
    def getResourceSet(self):
        """
        Grab all the Ids from redis set for this resource.
        """
        return list(self.r.smembers(self.resource_set))

    def idBySearchKey(self, key):
        """
        This is an alternate way to get the ID of a resource.

        If you have a field that is unique (such as a blog post slug)
        you can find the post ID that.

        i.e. example:slug:some-slug == 3
        3 is the post ID.
        """
        if not self.resource_search_key:
            raise NoOrmError(
                'You need to define resource_search_key '
                'in order to use this method.'
            )

        search_key = self._build_search_key(key)
        return self.r.get(search_key)

    def loadBySearchKey(self, key):
        if not self.resource_search_key:
            raise NoOrmError(
                'You need to define resource_search_key '
                'in order to use this method.'
            )

        search_key = self._build_search_key(key)

        return self.load(self.r.get(search_key))


    def setSearchKey(self, key, id):
        """
        This build and sets the search key and value

        For instance: if you have a user resource, and need
        the ability to get a uid by username, set your class'
        search_key to username.

        rendered search key will look like the following is the
        next userId is 1002...
        user:username:carl1 = 1002
        """
        search_key = self._build_search_key(key)
        return self.set(search_key, id)

    def _build_search_key(self, name):
        return '%s:%s:%s' % (
            self.resource_name,
            self.resource_search_key,
            str(name)
        )
