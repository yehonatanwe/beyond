import consts
import json
from logging import getLogger
from os import path


logger = getLogger(consts.LOGGER)


class Cacher:

    def __init__(self, cache_file):
        self.cache = {}
        self.cache_file = cache_file
        self.load_cache()

    def __del__(self):
        self.store_cache()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.store_cache()

    def load_cache(self):
        logger.debug('Loading cache')
        if path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.cache.update(json.load(f))
        else:
            self.cache = {}

    def store_cache(self):
        # logger.debug('Storing cache')
        if self.cache:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)

    def search_cache(self, key):
        logger.debug(f'Searching cache for key {key}')
        return self.cache.get(key)

    def update_cache(self, entry):
        logger.debug(f'Updating cache with entry: {json.dumps(entry)}')
        self.cache.update(entry)
        # self.store_cache()
