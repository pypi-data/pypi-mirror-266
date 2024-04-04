import redis

class RedisMixin(object):
    """
    Use Redis as storage for state of LLM agents
    """

    def connect_to_redis(self, creds):
        # connect to redis
        host = creds.get('host', 'localhost')
        port = creds.get('port', 6379)

        r = redis.Redis(host=host,
                        port=port,
                        decode_responses=True)

        return r

    def store_state_redis(self, statekey, state, creds={}):
        # connect to redis
        r = self.connect_to_redis(creds)
        # set the state
        result = r.set(statekey, state)

        return result

    def retrieve_state_redis(self, statekey, creds={}):
        # connect to redis
        r = self.connect_to_redis(creds)
        # get the state
        state = r.get(statekey)

        return state
