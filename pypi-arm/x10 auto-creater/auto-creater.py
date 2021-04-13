#!/usr/bin/env python3
# '''TODO'''

import json
import os
from os import path
import click
from pathlib import Path
import re
# from dotenv import load_dotenv
import requests

PATH=os.path.dirname(os.path.abspath(__file__)) + os.path.sep
PATH_0=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.path.sep
FILE='data.json'
TEMPLATE='template simple.html'
print(PATH, PATH_0, FILE)

@click.command()
@click.option("-n", "--no-cache", default=False, is_flag=True, help=f"force reload, even if {FILE} exists")
def main(no_cache):
    ''' TODO '''
    
    res = {}
    data = get_data(no_cache)
    for value in data:
        # normalize package-name .-_ -> -
        norm_name = normalize(value['name'].split('-')[0])
        # create dict with all files as list per normalized name
        res.setdefault(norm_name, []).append((value['name'],value['download_url']))
    # print(res)
    # create folder for all packages (if not exists)
    for key in res.keys():
        if not os.path.exists(PATH_0 + key):
            print("creating folder", key)
            os.makedirs(PATH_0 + key)
        print("processing", key)
        write_html(key, res[key])

def write_html(pkg, items):
    '''create html file from template with name and url'''
    tag = ""
    print("\t..creating " + pkg +".html")
    for obj in items:
        print('\t\t..version=', obj[0])
        tag += f'\t\t\t<li><a href="{obj[1]}">{obj[0]}</a></li>\n'

    fin = open(PATH + TEMPLATE, "rt")
    #read file contents to string
    tmpl = fin.read()
    #replace all occurrences of the required string
    tmpl = tmpl.replace('### replace_string', tag)
    tmpl = tmpl.replace('### title', pkg)
    #close the input file
    fin.close()
    #open the input file in write mode
    fin = open(PATH_0 + os.path.sep + pkg + os.path.sep + 'index.html', "wt")
    #overrite the input file with the resulting data
    fin.write(tmpl)
    #close the file
    fin.close()
    
def get_data(no_cache):
    if not path.exists(PATH + FILE):
        # print("not existing")
        data = load_url()
    else:
        if no_cache:
            # print("exists nocache")
            data = load_url()
        else:
            # print("exists")
            data = read_json()
    return data

def load_url():
    print('loading from github api')
    req = requests.get('https://api.github.com/repos/trasba/pypi-arm/contents/wheels')
    data = req.json()
    with open(PATH + FILE, 'w') as outfile:
        json.dump(data, outfile)
    return data

# curl   -H "Accept: application/vnd.github.v3+json"   https://api.github.com/repos/trasba/pypi-arm/contents/wheels > pypi

def read_json():
    print('reading from existing file')
    with open(PATH + FILE) as json_file:
        data = json.load(json_file)
    return data

def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()

if __name__ == "__main__":
    main() # pylint: disable=no-value-for-parameter
