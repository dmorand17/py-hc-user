import os
from pathlib import Path
import shutil
import argparse
import datetime
from collections import OrderedDict
from csv_utils.csv_handler import CSVHandler
from csv_utils.csv_jinja import CSVJinja

def print_debug(msg):
    if(debug == True):
        print("[DEBUG]\t{0}".format(msg))

def parse_args():
    parser = argparse.ArgumentParser(description='This script will generate a file based on a template and csv file')
    parser.add_argument('-v','--verbose', help='Enable verbose logging', action='store_true')
    parser.add_argument('-i', '--input', help='input file containing mapping to be used in template', required=True, action='store')
    parser.add_argument('--template-dir', help='template directory to find templates', default='templates', action='store')    
    parser.add_argument('-t', '--templates', help='template filename', required=True, action='store', nargs='+')
    return parser.parse_args()


def validate_args(main_args):
    global debug
    debug = main_args.verbose
    if not os.path.isfile(main_args.input):
        raise SystemExit("input file does not exist: {0}".format(main_args.input))    

class User():
    def __init__(self, name, *args, **kwargs):
        self.name=name
        self.templates = OrderedDict()

    def add_template(self, template, rendered=None):
        self.templates.update({template:rendered})
    
class HealthcloudUserCSVJinja():
    
    def __init__(self,csv_file,templates,template_dir="templates"):
        self.templates = templates
        self.users = []

        csv_handler = CSVHandler(csv_file)
        self.csv = csv_handler.rows()

        env_options = {
            'trim_blocks':True
            ,'lstrip_blocks':True
        }

        # Create CSVJinja
        self.csvjinja = CSVJinja(env_options=env_options,template_path=template_dir)
        self.csvjinja.add_filters({
            'map_role':self.map_role
        })
        self.csvjinja.add_globals({
            'utcnow':datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        })

    def map_role(self,role):
        role_mapping = {
            'HS - Clinical':'Level 1 - Primary Provider'
            ,'Health Sphere Group 1- Level 7a':'Level 7a - Horizon Standard Internal User'
        }
        return role_mapping.get(role.strip(),None)

    def _filter_csv(self,filters):
        # print("Rows before: {}".format(str(len(self.csv))))
        # env='SIT'
        # self.csv = list(filter(lambda row: row[env] == "Y",self.csv))
        # print("Rows after: {}".format(str(len(self.csv))))

        for fltr in filters:
            print("Rows before: {}".format(str(len(self.csv))))
            self.csv = list(filter(fltr,self.csv))
            print("Rows after: {}".format(str(len(self.csv))))
        return self.csv

    def render_csv(self,filters):
        for i,row in enumerate(self._filter_csv(filters),start=1):
            user = User(row['HS User Name'])

            for template in self.templates:
                # rendered = csvjinja.render_template(template,row,template_globals={'utcnow':datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"})
                rendered = self.csvjinja.render_template(template,row)
                user.add_template(template,rendered=rendered)
            
            self.users.append(user)

    def write_outputfiles(self):
        o = Path("output")
        if o.is_dir():
            shutil.rmtree("output")
        o.mkdir()

        template_file = {}
        for template in self.templates:
            template_file[template] = {
                "basefile":os.path.splitext(template)[0]
                ,"ext":os.path.splitext(template)[1]
            }

        for user in self.users:
            for template,rendered in user.rendered_template.items():
                with open("output/"+template_file[template].get("basefile") + "_rendered_{}".format(i) + template_file[template].get("ext"),"w") as outputFile:
                    outputFile.write(rendered)

def main():
    args = parse_args()
    validate_args(args)

    if debug:
        print("capturing errors...")
        p = Path("errors")
        if p.is_dir():
            shutil.rmtree("errors")
        p.mkdir()

    converter = HealthcloudUserCSVJinja(args.input,args.templates,args.template_dir)
    converter.render_csv()
    for user in converter.users:
        print (user.templates)
        [print("template: {}\nrendered: {}".format(template,rendered)) for template,rendered in user.templates.items()]
"""
Execution Script
"""
if __name__ == '__main__':
    main()