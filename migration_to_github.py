import sys
import requests
import configparser
from string import Template
import json

config = configparser.ConfigParser(allow_no_value=True)
config.read('config.ini')
print (config.sections())

github_config={}
github_config['auth']=(config['github']['username'],config['github']['password'])
github_config['headers']={
  "Accept": "application/vnd.github.barred-rock-preview",
  "user-agent": "my-app/0.0.1"
}


base_url=Template(config['migration_from']['base_url'])

paiload={
  "vcs": config['migration_from']['type'],
  "vcs_url": None,
  "vcs_username": config['migration_from']['username'],
  "vcs_password": config['migration_from']['password']
}

github_headers={
  "Accept": "application/vnd.github.barred-rock-preview",
  "user-agent": "my-app/0.0.1"
}

def github_repo(url,auth):
    if url[-1] == '/':
        url=url[:-1]
    r = requests.get(url,auth=auth)
    if r.status_code >= 200 and r.status_code <300:
        return True
    else:
        return False


def github_import(paiload, github_config): #Paiload & github_config
    pl=json.dumps(paiload)
    gc=github_config

    tmp_url=Template("https://api.github.com/repos/$USER/$REPO/$OPER")
    url=tmp_url.substitute(USER=gc['auth'][0],REPO=gc['migration_to'],OPER="")
    url_import = tmp_url.substitute(USER=github_config['auth'][0], REPO=gc['migration_to'], OPER="import")

    if github_repo(url,gc['auth']):
        r = requests.get(url_import,headers=gc['headers'],auth=gc['auth'])
        if r.status_code == 404:
            ra = requests.put(url_import,pl,headers=gc['headers'],auth=gc['auth'])
            if ra.status_code == 200:
                print ("Create new import GOOD for "+url_import)
            else:
                print ("Create new import FAIL for "+url_import)

        elif r.status_code == 200:
            ra = requests.patch(url_import,pl,headers=gc['headers'],auth=gc['auth'])
            if ra.status_code == 200:
                print ("Patch import GOOD for "+url_import)
            else:
                print ("Patch import FAIL for "+url_import)
        else:
            print ("Unknown status code "+url_import)
    else:
        print("GirHub REPO not exists: "+url)

for migration_from in config['migration']:
    migration_to=config['migration'][migration_from]
    if migration_to is None:
        migration_to=migration_from
    paiload['vcs_url']=base_url.substitute(REPO=migration_from)
    github_config['migration_to']=migration_to
    github_import(paiload,github_config)

sys.exit(0)