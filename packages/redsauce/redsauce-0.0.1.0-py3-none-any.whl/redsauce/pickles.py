from redis import Redis as BaseRedis

class Redis(BaseRedis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_args = args
        self.redis_kwargs = kwargs
    def __getstate__(self):
        state = {'redis_args': self.redis_args, 'redis_kwargs': self.redis_kwargs}
        return state
    def __setstate__(self, state):
        self.__dict__.update(state)
        super().__init__(*self.redis_args, **self.redis_kwargs)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass