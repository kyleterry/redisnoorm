from redisnoorm import RedisResourceBase

class Example(RedisResourceBase):
    redis_host = 'localhost'
    redis_port = 6381

    # name of the resource (object)
    resource_name = 'example'

    # name of the INCR id for this resource
    # kind of like a sql Primary Key that
    # auto increments.
    resource_next_id = 'example:id'

    # a set of IDs that exist as resources.
    resource_set = 'example:set'

    # this is a custom search key. this key will look like so...
    # example:slug:some-slug-yay = 17
    # 17 is the example id.
    resource_search_key = 'slug'
    
    # these are the field keys that belong to your resource.
    # %s is where the orm will plug the resource ID into.
    # example: "table name"
    # %s: "resource Id"
    # title, body...: "table" "field"
    field_keys = {'title': 'example:%s:title'
                , 'body': 'example:%s:body'
                , 'slug': 'example:%s:slug'
                , 'created': 'example:%s:created'
    }

    """
    If you needed other functionality, you can build 
    more methods like the following. This one gives
    this resource the ability to associate with tags.

    Eventually I will build a connector.
    """
    tag_set = 'example:%s:tags'

    def setTags(self, tag_id=None):
        if tag_id is None: 
            raise Exception("tag_id cannot be None")

        if type(tag_id).__name__=='str' \
            or type(tag_id).__name__=='unicode' \
            or type(tag_id).__name__=='int':
            
            tag_id = [tag_id]

        for t in tag_id:
            # check if that key is already a member of the
            # tag set.
            if not self.isMember(self.tag_set, t, self.id):
                # if not, go ahead and set it as a new member.
                self.pushToSet(self.tag_set, t, self.id)

# useage:
"""
example = Example().load(3)
if example:
    ...
OR
example.loadBySearchKey('some-slug-yay')
OR to save a new record:
example = Example()
example.title = 'some title'
example.body = 'some text body'
example.slug = 'some-title'
example.created = datetime.datetime.now()
example.save()
"""
