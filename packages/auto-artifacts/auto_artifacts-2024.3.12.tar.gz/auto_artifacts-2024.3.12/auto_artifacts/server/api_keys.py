import os
import json

import auto_artifacts.server.config as config

global keys
with open(config.PATH_API_KEYS, 'r') as j:
    raw = j.read()
keys = json.loads(raw)

global orgs
with open(config.PATH_ORGS, 'r') as j:
    raw = j.read()
orgs = json.loads(raw)

global projects
with open(config.PATH_PROJECTS, 'r') as j:
    raw = j.read()
projects = json.loads(raw)

def validate(path):

    invalids = [
        "..",
        ".env"
    ]

    for invalid in invalids:
        if invalid in path:
            return False

    if "/" in path:
        org = path.split("/")[0]
        project = path.split("/")[1]
        if org in orgs['orgs'] and project in projects['projects'] :
            return True

    return False

def auth(key, path):

    with open(config.PATH_API_KEYS, 'r') as j:
        raw = j.read()
    keys = json.loads(raw)

    org = path.split("/")[0]
    project = path.split("/")[1]

    if key in keys.keys():
        key_orgs = keys[key]['orgs']
        key_projects = keys[key]['projects']
        if org in orgs['orgs'] and project in projects['projects']:
            if org in key_orgs and project in key_projects:
                return True

    return False


