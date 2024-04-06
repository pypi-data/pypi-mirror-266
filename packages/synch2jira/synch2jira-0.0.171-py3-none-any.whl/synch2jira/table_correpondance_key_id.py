import json
import config
from synch2jira.issue_S2 import IssueS2


def save_correspondence(key, id):
    try:

        table = get_correspondence_table()
    except FileNotFoundError:
        table = {}
    table[key] = id

    with open(config.table_correspondance_file, 'w') as f:
        json.dump(table, f)


def save_correspondence_dict(correspondence_dict):
    try:
        table = get_correspondence_table()
    except FileNotFoundError:
        table = {}
    table.update(correspondence_dict)

    with open(config.table_correspondance_file, 'w') as f:
        json.dump(table, f)


def get_correspondence_table():
    try:
        with open(config.table_correspondance_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(config.table_correspondance_file, 'w') as f:
            json.dump({}, f)
        return {}


def get_correspondance(id):
    table = get_correspondence_table()
    return table[id]


def save_correspondance_table(key, id):
    if not verifier_existence_key(key) and not verifier_existence_id(id):
        data = get_correspondence_table()
        nouvelle_entree = {"key": key, "id": id}
        data.append(nouvelle_entree)
        with open(config.table_correspondance_file, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    return False


def verifier_existence_key(key):
    data = get_correspondence_table()
    for entry in data:
        if entry.get("key") == key:
            return True
    return False


def verifier_existence_id(id):
    data = get_correspondence_table()
    for entry in data:
        if entry.get("id") == id:
            return True
    return False


def supprimer_key_id(key=None, id=None):
    data = get_correspondence_table()
    if key is not None or id is not None:
        for entry in data:
            if entry.get("key") == key or entry.get("id") == id:
                data.remove(entry)
                with open(config.table_correspondance_file, 'w') as f:
                    json.dump(data, f, indent=4)
                return True
    return False


def rebuild_correspondence_table():
    jql_query = f" s1_id is not  null "
    issue_list = IssueS2.find_by(jql_query)
    data = {}
    for issue in issue_list:
        key = issue['key']
        id = issue['fields'][config.s1_id_in_jira]
        data[key] = id
        with open(config.table_correspondance_file, 'w') as f:
            json.dump(data, f, indent=4)
