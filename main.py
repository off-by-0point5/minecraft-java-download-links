import requests
import time
from bs4 import BeautifulSoup
import json
from pathlib import Path
import os
from datetime import datetime, timedelta

online = True
timeout = 10
sites_root = './sites/'

last_download = 0


def get_html(url: str):
    global last_download
    print(url + ' -> ', end='')
    url = url[1:]
    p = Path(sites_root).joinpath(url)
    try:
        with p.joinpath('html').open('r') as f:
            html = f.read()
            print('read from file')
    except FileNotFoundError:
        if online:
            sleep_time = (last_download + timeout) - datetime.utcnow().timestamp()
            if sleep_time > 0:
                print(f'Sleep {sleep_time} seconds.')
                time.sleep(sleep_time)
            html = requests.get(web_root + url).text
            last_download = datetime.utcnow().timestamp()
            if not p.exists():
                p.mkdir(parents=True)
            with p.joinpath('html').open('w') as f:
                f.write(html)
                print('downloaded')
        else:
            html = ''
    return html


web_root = 'https://mcversions.net/'
# Map Tag keys to strings
group_names = ['stable', 'snapshot', 'beta', 'alpha']
group_keys = []
# List of version html tags
tag_list = []
# Dict of versions
versions_list = []
versions_tree = {}

with open('versions-list.json', 'rt') as file:
    versions_list = json.loads(file.read())

soup = BeautifulSoup(get_html('/'), "html.parser")
all_divs = soup.find_all('div')
for div in all_divs.copy():
    if div.get('id') is None or div.get('data-version') is None:
        all_divs.remove(div)

for d in all_divs:
    if d.parent not in group_keys:
        group_keys.append(d.parent)
        versions_tree[group_names[group_keys.index(d.parent)]] = []
    tag_list.append(d)
    versions_tree[group_names[group_keys.index(d.parent)]].append(tag_list.index(d))
for version in tag_list:
    # print(version)  # print html tag found for version
    download_link = version.find('a').get('href')
    version = {'date': version.find('time').text,
               'type': group_names[group_keys.index(version.parent)],
               'version': version.get('data-version')}
    for indexed_version in versions_list:
        if version['version'] == indexed_version['version']:
            print(f"{version['version']} already indexed.")
            break
    else:
        download_soup = BeautifulSoup(get_html(download_link), "html.parser")
        binaries = download_soup.find_all('a')
        binary_locations = {}
        for b in binaries:
            if b.get('href').endswith('client.jar'):
                binary_locations['client'] = b.get('href')
            if b.get('href').endswith('server.jar'):
                binary_locations['server'] = b.get('href')
        version.update(binary_locations)
        versions_list.append(version)
        # print(version)  # print versin json


versions_tree = {}
for version_dict in versions_list:
    if version_dict['type'] not in versions_tree:
        versions_tree[version_dict['type']] = {}
    versions_tree[version_dict['type']][version_dict['version']] = version_dict

with open('versions-tree.json', 'w') as file:
    file.write(json.dumps(versions_tree, indent=2))
with open('versions-list.json', 'w') as file:
    versions_list = sorted(versions_list, key=lambda k: k['date'], reverse=True)
    file.write(json.dumps(versions_list, indent=2))
os.system('rm -r ./sites/*')
