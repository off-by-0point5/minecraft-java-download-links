import requests
import time
from bs4 import BeautifulSoup
import json
from pathlib import Path
import os

online = True
timeout = 10
sites_root = './sites/'


def get_html(url: str):
    print(url + ' -> ', end='')
    url = url[1:]
    p = Path(sites_root).joinpath(url)
    try:
        with p.joinpath('html').open('r') as f:
            html = f.read()
            print('read from file')
    except FileNotFoundError:
        if online:
            html = requests.get(web_root + url).text
            if not p.exists():
                p.mkdir(parents=True)
            with p.joinpath('html').open('w') as f:
                f.write(html)
                print('downloaded')
            time.sleep(timeout)
        else:
            html = ''
    return html


web_root = 'https://mcversions.net/'
versions_json = {}
versions_list = []
versions_path = Path('versions.json')
if versions_path.is_file():
    with versions_path.open('r') as file:
        versions_json = json.loads(file.read())
soup = BeautifulSoup(get_html('/'), "html.parser")
versions = soup.find('div', {'class': 'versions'})
named_types = versions.find_all('div', recursive=False)
c1 = 0
for n in named_types:
    c1 += 1
    name = n.find('h5').get('class')[0]
    if not versions_json.get(name):
        versions_json[name] = {}
    n = n.find('div', {'class': 'items'}).find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['item'])
    c2 = 0
    for e in n:
        c2 += 1
        dl_link_site = e.find('a', {'class': 'button'}).get('href')
        item = e.get('id')
        release_time = e.find('time').text
        print(str(c1)+'/'+str(len(named_types))+' | '+str(c2)+'/'+str(len(n))+' | ', end='')
        list_item = {
            'date': release_time,
            'type': name,
            'version': item,
        }
        if not versions_json[name].get(item):
            versions_json[name][item] = {}
            dl_soup = BeautifulSoup(get_html(dl_link_site), "html.parser")
            downloads = dl_soup.find_all('div', {'class': 'download'})
            for d in downloads:
                if d.find('h5'):
                    side = d.find('h5').text.split(' ')[0].lower()
                    dl_link = d.find('a', {'class': 'button'}).get('href')
                    versions_json[name][item][side] = dl_link
                    list_item[side] = dl_link
        else:
            print('indexed')
            for side in versions_json[name][item]:
                if side in ['server', 'client']:
                    list_item[side] = versions_json[name][item][side]
        versions_json[name][item]['date'] = release_time
        versions_list.append(list_item)

with open('versions.json', 'w') as file:
    # print(json.dumps(versions_json, indent=2))
    file.write(json.dumps(versions_json, indent=2))
with open('versions-list.json', 'w') as file:
    versions_list = sorted(versions_list, key=lambda k: k['date'], reverse=True)
    file.write(json.dumps(versions_list, indent=2))
os.system('rm -r ./sites/*')
