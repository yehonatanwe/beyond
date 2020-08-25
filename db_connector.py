import consts
import csv
import os
from logging import getLogger


logger = getLogger(consts.LOGGER)


class DbConnector:

    def __init__(self, db_path, db_format='csv'):
        self.db_path = db_path
        self.db_format = db_format
        if self.validate_path():
            raise Exception(f'DB path does not exist {self.db_path}')
        if self.validate_format():
            raise Exception(f'Unknown DB format: {self.db_format}')
        self.db = None

    def validate_path(self):
        return not os.path.exists(self.db_path)

    def validate_format(self):
        return self.db_format not in consts.KNOWN_DB_FORMATS

    def load_db(self):
        if not self.db:
            logger.debug(
                f'Attempting to load {self.db_format} DB from {self.db_path}')
            self.db = {
                'csv': self.load_csv_db()
            }.get(self.db_format)
        return self.db

    def load_csv_db(self):
        logger.info(f'Loading csv DB from {self.db_path}')
        return [dict(r) for r in csv.DictReader(open(self.db_path))]
