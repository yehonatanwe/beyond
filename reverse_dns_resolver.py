import consts
import socket
from cacher import Cacher
from logging import getLogger


logger = getLogger(consts.LOGGER)


class ReverseDNS:

    def __init__(self):
        self.cache = Cacher(consts.REVERSE_DNS_CACHE)

    def __del__(self):
        self.cache.store_cache()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cache.store_cache()

    def get_domain(self, ip):
        if not ip:
            return None
        domain = self.cache.search_cache(ip)
        if domain is not None:
            logger.debug(f'Domain for {ip} found in cache')
            return domain
        try:
            logger.debug(f'Resolving DNS for: {ip}')
            domain = socket.gethostbyaddr(ip)[0]
            self.cache.update_cache({ip: domain})
        except socket.herror:
            self.cache.update_cache({ip: ''})
            return None
