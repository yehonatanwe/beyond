#!/usr/bin/env python3


import argparse
import json
from db_connector import DbConnector
from fw_connector import FwConnector
from fw_db_comparator import FwDbComparator


def parse_arguments():
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
    fw = FwConnector(args.fw_logs)
    comparator = FwDbComparator(db.get_list_db())
    for fw_logs in iter(fw):
        comparator.compare_records(fw_logs)
    print(json.dumps(comparator.matches, indent=2))


if __name__ == '__main__':
    main()
