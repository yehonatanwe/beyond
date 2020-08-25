#!/usr/bin/env python3


import argparse
import consts
import json
import logging.handlers
from db_connector import DbConnector
from fw_connector import FwConnector
from fw_db_comparator import FwDbComparator
from multiprocessing.dummy import Pool


logging.basicConfig(filename=consts.LOGFILE,
                    format=consts.LOGGER_FORMAT,
                    level=logging.DEBUG)
logging.handlers.RotatingFileHandler(consts.LOGFILE, mode='a',
                                     maxBytes=consts.LOGFILE_SIZE,
                                     backupCount=2)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(consts.LOGGER_FORMAT))
console_handler.setLevel(logging.DEBUG)
logger = logging.getLogger(consts.LOGGER)
logger.addHandler(console_handler)


def parse_arguments():
    logger.debug('Parsing arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--db-path', default='ServiceDBv1.csv',
                        dest='db_path', help='Path to DB')
    parser.add_argument('-f', '--filters', dest='filters',
                        help='Comparison filters', type=list)
    parser.add_argument('-l', '--fw-logs', default='firewall.log',
                        dest='fw_logs', help='Path to FW logs')
    return parser.parse_args()


def main():
    args = parse_arguments()
    db = DbConnector(args.db_path)
    fw = FwConnector(args.fw_logs, args.filters)
    comparator = FwDbComparator(db.load_db())
    # pool = Pool(consts.THREAD_POOL_SIZE)
    # pool.imap(comparator.compare_records, iter(fw), chunksize=10)
    # pool.close()
    # pool.join()
    with Pool(consts.THREAD_POOL_SIZE) as pool:
        for _ in pool.imap(comparator.compare_records, iter(fw), chunksize=10):
            pass
    print(json.dumps(comparator.matches, indent=2))


if __name__ == '__main__':
    main()
