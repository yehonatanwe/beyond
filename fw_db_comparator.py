import consts
import json
from logging import getLogger
from multiprocessing.dummy import Pool


logger = getLogger(consts.LOGGER)


class FwDbComparator:

    def __init__(self, db_records, filters=None):
        self.db_records = db_records
        self.filters = filters
        self.matches = {k['Service name']: 0 for k in db_records}

    def compare_record(self, fw_log):
        for r in self.db_records:
            if r['Service domain'] in getattr(fw_log, 'DOMAIN', ''):
                return r['Service name']

    def compare_records(self, fw_logs):
        logger.debug('Starting comparison cycle')
        with Pool(consts.THREAD_POOL_SIZE) as pool:
            results = pool.map(self.compare_record, fw_logs)
        for r in results:
            if r in self.matches:
                self.matches[r] += 1
        logger.debug(f'current matches: {json.dumps(self.matches)}')
