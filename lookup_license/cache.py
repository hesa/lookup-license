from pathlib import Path
from diskcache import Cache

class LookupLicenseCache():

    def __init__(self):
        self.cache = None

    def _init_cache(self):
        if not self.cache:
            self.cache = Cache(f'{Path.home()}/.ll/')

    def add(self, key, value):
        self._init_cache()
        self.cache.add(key, value)
    
    def close(self):
        self._init_cache()
        self.cache.close()
    
    def __new__(cls):
        if not hasattr(cls, 'llcache'):
            cls.llcache = super(LookupLicenseCache, cls).__new__(cls)
        return cls.llcache

    def list(self):
        self._init_cache()
        return list(self.cache)


cache = LookupLicenseCache()
cache = LookupLicenseCache()
cache = LookupLicenseCache()
cache = LookupLicenseCache()
cache = LookupLicenseCache()

cache.add("hesa", "ksksk")

print(str(cache.list()))

cache.close()
