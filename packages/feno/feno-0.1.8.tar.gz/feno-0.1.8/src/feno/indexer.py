#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re
import argparse
from os.path import  isfile


def update_titles(path):
    with open(path, 'r') as file:
        content = file.read()

    lines = content.split('\n')

    output = []

    for line in lines:
        new_description = 'New description'
        match = re.search(r'\[(.*?)\]\((.*?)\)', line)
        data = line
        if match:
            link = match.group(2)
            if link.endswith('md') and not link.startswith('http'):
                if not isfile(link):
                    print(link, ' not found')
                else:
                    header = open(match.group(2), 'r').read().split('\n')[0]
                    if (len(header) == 0):
                        print('Empty header in ', link)
                    # remove first word
                    try:
                        header = header.split(' ', 1)[1]
                    except:
                        print('Error ', header)
                        pass
                    new_description = header
                    #print(new_description)
                    #replace line with new description
                    data = line.replace(match.group(1), new_description)
        output.append(data)

    with open(path, 'w') as file:
        file.write('\n'.join(output))

def check_labels_ok(path) -> bool:
    with open(path, 'r') as file:
        data = file.read()
        lines = data.split('\n')

        ok = []
        not_ok = []

        for line in lines:
            if "/Readme.md)" in line and not "https:" in line:
                #print(line)
                try:
                    label = line.split('@')[1].split(' ')[0].split(']')[0]
                except:
                    print("error in", line)
                    continue
                hook = line.split('base/')[1].split('/')[0] 
                output = "    " + label + ("==" if label == hook else " != ") + hook
                if label == hook:
                    ok.append(output)
                else:
                    not_ok.append(output)

        print("verified:", len(ok))
        print("mismatch:", len(not_ok))
        for line in not_ok:
            print(line)
        return len(not_ok) == 0

def main(): 
    parser = argparse.ArgumentParser(description='Indexer')
    parser.add_argument('path', type=str, help='Path to Markdown file')

    args = parser.parse_args()

    update_titles(args.path)
    if not check_labels_ok(args.path):
        exit(1)

if __name__ == '__main__':
    main()    