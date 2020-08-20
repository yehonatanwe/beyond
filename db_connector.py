import csv
import os


KNOWN_DB_FORMATS = ['csv']


class DbConnector:

    def __init__(self, db_path, db_format='csv'):
        self.db_path = db_path
        self.db_format = db_format
        if self.validate_path():
            raise Exception(f'DB path does not exist {self.db_path}')
        if self.validate_format():
            raise Exception(f'Unknown DB format: {self.db_format}')
        self.list_db = None

    def validate_path(self):
        return not os.path.exists(self.db_path)

    def validate_format(self):
        return self.db_format not in KNOWN_DB_FORMATS

    def get_list_db(self):
        if not self.list_db:
            self.list_db = {
                'csv': self.read_csv_db()
            }.get(self.db_format)
        return self.list_db

    def read_csv_db(self):
        print(f'loading db from {self.db_path}')
        return [dict(r) for r in csv.DictReader(open(self.db_path))]
