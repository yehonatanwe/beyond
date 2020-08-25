import consts
import json
import os
from fw_logs_filter import FwLogFilterApplier
from logging import getLogger
from multiprocessing.dummy import Pool
from reverse_dns_resolver import ReverseDNS


logger = getLogger(consts.LOGGER)


class FwLogEntry:

    def __init__(self, log_str):
        self.log_str = log_str
        for attr in log_str.split():
            k, _, v = attr.partition('=')
            self.__dict__.update({k: v})

    def __hash__(self):
        return hash(self.log_str)

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)


class FwConnector:

    def __init__(self, fw_path, filters=None, chunk=consts.CHUNK):
        self.fw_path = fw_path
        if self.validate_path():
            raise Exception(f'FW path does not exist {self.fw_path}')
        self.fw_fd = open(self.fw_path, 'r')
        self.resolver = None
        self.filters = FwLogFilterApplier(filters)
        self.chunk = chunk

    def __del__(self):
        self.fw_fd.close()

    def __iter__(self):
        return self

    def __next__(self):
        logger.debug('Loading next chunk of FW logs')
        logs = self.fw_fd.readlines(self.chunk)
        if not logs:
            raise StopIteration
        with ReverseDNS() as self.resolver:
            with Pool(consts.THREAD_POOL_SIZE) as pool:
                list_log = list(
                    filter(None, set(pool.map(self.process_log_entry, logs))))
        return list_log or []

    def validate_path(self):
        return not os.path.exists(self.fw_path)

    def process_log_entry(self, log_str):
        entry = FwLogEntry(log_str)
        if self.filters.filter_log(entry):
            return None
        if not hasattr(entry, 'DOMAIN'):
            if not hasattr(entry, 'SRC'):
                return entry
            domain = self.resolver.get_domain(getattr(entry, 'SRC', None))
            if domain:
                entry.DOMAIN = domain
        return entry
