import os
import sys
import argparse
import csv
import datetime
from pathlib import Path
import shutil
import logging

import requests
import xml.etree.ElementTree as ET
import urllib3

from healthcloud_user_csvjinja import HealthcloudUserCSVJinja

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create logger
logging.basicConfig()
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description='This script will create users in portal and reset their password.')
    parser.add_argument('-v','--verbose', help='Enable verbose logging', action='count', default=0)
    parser.add_argument('-i', '--input', help='input file containing mapping to be used in template', required=True, action='store')
    parser.add_argument('--hostname', help='Environment to perform changes to (e.g. localhost)', required=True, default="localhost", action='store', nargs='+')
    parser.add_argument('--env', help='environment to build (e.g. SIT, UAT, PROD)', required=True, action='store', choices=["SIT","UAT","PROD"])
    return parser.parse_args()

def validate_args(main_args):
    if not os.path.isfile(main_args.input):
        raise SystemExit("input file does not exist: {0}".format(main_args.input))

def send_request(output,host,error_file_pfx):
    ns = {'web': 'http://webservices.ht.carecom.dk/',
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/'}

    url = "https://{}:19043/ws/UserManagementServiceSei?wsdl".format(host)
    
    try:
        r = requests.post(url, data=output, verify=False)
        # print(r.content)
        responseRoot = ET.fromstring(r.content.decode('utf-8',errors='ignore'))
        # Check for a Soap Fault
        faultstring = responseRoot.find('.//faultstring',namespaces=ns)
        # print("faultstring {}".format(faultstring.text))
        if faultstring is not None and logger.isEnabledFor(logging.INFO):
            logger.debug("error occurred: {}".format(faultstring.text))
            with open("./errors/" + error_file_pfx +"-error.log","w+") as errorFile:
                errorFile.write(output + "\n\n")
                errorFile.write(r.content.decode('utf-8',errors='ignore'))
        
        return r.status_code
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        logger.exception("Exception occurred")
        sys.exit()

def filter_env(row,env):
    return row[env] == "Y"

def main():
    args = parse_args()
    validate_args(args)

    log_level = {
        2: logging.DEBUG
        ,1: logging.INFO
        ,0: logging.CRITICAL 
    }
    logger.setLevel(log_level[args.verbose])

    if logger.isEnabledFor(logging.INFO):
        logger.info("capturing errors")
        p = Path("errors")
        if p.is_dir():
            shutil.rmtree("errors")
        p.mkdir()

    templates = ["create-user-v2.j2","reset-userpassword-v2.j2"]
    converter = HealthcloudUserCSVJinja(args.input,templates)
    
    filters = [lambda row: filter_env(row,args.env)]
    converter.render_csv(filters)

    # Send requests into environment
    for i,user in enumerate(converter.users,start=1):
        print("{}. user: {}".format(i,user.name))
        for t,v in user.templates.items():
            print(" - template: {}".format(t))
            for host in args.hostname:
                status = send_request(v,host,error_file_pfx=user.name)
                print("   host:{}, status:{}".format(host,"error" if status is None else status))
        print("======================================================================================================")
"""
Execution Script
"""
if __name__ == '__main__':
    
    main()