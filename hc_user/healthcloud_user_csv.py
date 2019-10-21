import os
import argparse
import csv
import hashlib
from csv_utils.csv_handler import CSVHandler, InputDelim

def generate_pw(pw, salt):
    return hashlib.md5(pw.encode()).hexdigest()

def print_debug(msg):
    if(debug == True):
        print("[DEBUG]\t{0}".format(msg))

def parse_args():
    parser = argparse.ArgumentParser(description='This script will generate a file based on a template and csv file')
    parser.add_argument('-v','--verbose', help='Enable verbose logging', action='store_true')
    parser.add_argument('-i', '--input', help='input file containing mapping to be used in template', required=True, action='store')
    parser.add_argument('-d', '--delim', help='input delimiter used to split data', default='comma', action='store', type=InputDelim, choices=list(InputDelim))
    parser.add_argument('-s', '--salt', help='salt used in generating password', required=True, action='store')
    return parser.parse_args()

# for testing only
def update_program(row):
    # print(kwargs)
    return row['Lan ID'] + '---PROGRAM----' + generate_pw('---PROGRAM----','12345')

def validate_args(main_args):
    global debug
    debug = main_args.verbose
    if not os.path.isfile(main_args.input):
        raise SystemExit("input file does not exist: {0}".format(main_args.input))

def update_csv(main_args):
    csv_updater = CSVHandler(main_args.input)

    # Update the row with the following
    '''
    row['HS User Name'] = 'HZN.' + row['Lan ID']
    row['HS Password'] = generate_pw(row['Lan ID'],kwargs['salt'])
    '''

    csv_updates = {
        'HS User Name' : lambda row : ("HZN." + row['Lan ID'] if row['Lan ID'] != "" else row['HS User Name'])
        ,'HS Password' : lambda row : (generate_pw(row['Lan ID'],'Orionsy5') if row['Lan ID'] != "" else row['HS Password'])
    }

    csv_updater.update_rows(**csv_updates)
    csv_updater.write_csv()

def main():
    args = parse_args()
    validate_args(args)
    update_csv(args)

"""
Execution Script
"""

if __name__ == '__main__':
    main()