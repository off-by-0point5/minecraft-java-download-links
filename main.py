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
        print(str(c1)+'/'+str(len(named_types))+' | '+str(c2)+'/'+str(len(n))+' | ', end='')
        if not versions_json[name].get(item):
            versions_json[name][item] = {}
            dl_soup = BeautifulSoup(get_html(dl_link_site), "html.parser")
            downloads = dl_soup.find_all('div', {'class': 'download'})
            for d in downloads:
                if d.find('h5'):
                    versions_json[name][item][d.find('h5').text.lower().replace(' ', '_')] = \
                        d.find('a', {'class': 'button'}).get('href')
        else:
            print('indexed')
with open('versions.json', 'w') as file:
    file.write(json.dumps(versions_json))
os.system('rm -r ./sites/download/*')
os.system('rm -r ./sites/*')
