import os
from consts import CHUNK, THREAD_POOL_SIZE
from multiprocessing.dummy import Pool
from reverse_dns_resolver import get_domain


class FwConnector:

    def __init__(self, fw_path):
        self.fw_path = fw_path
        if self.validate_path():
            raise Exception(f'FW path does not exist {self.fw_path}')
        self.fw_fd = open(self.fw_path, 'r')

    def __del__(self):
        self.fw_fd.close()

    def __iter__(self):
        return self

    def __next__(self):
        logs = self.fw_fd.readlines(CHUNK)
        if not logs:
            raise StopIteration
        with Pool(THREAD_POOL_SIZE) as pool:
            list_log = pool.map(self.process_log_entry, logs)
        return list_log

    def validate_path(self):
        return not os.path.exists(self.fw_path)

    def process_log_entry(self, line):
        entry = {}
        for e in line.split():
            k, _, v = e.partition('=')
            entry[k] = v
        if 'DOMAIN' not in entry:
            domain = get_domain(entry['SRC'])
            if domain:
                entry['DOMAIN'] = domain
        return entry
