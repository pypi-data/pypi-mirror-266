import json

import requests
from requests.auth import HTTPBasicAuth

import config
from synch2jira.issue import Issue
from synch2jira.issue_S1 import IssueS1

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


class IssueS2(Issue):
    key: str

    def __init__(self, key=None, summary=None, description=None, updated=None, status_updated=None, status=None):
        Issue.__init__(self, summary, description, updated, status, status_updated)
        self.key = key
        if self.miror is not None:
            self.miror.miror = self

    def format_issue_into_json(self):
        issue = {
            "fields": {
                "description": {
                    "content": [
                        {
                            "content": [
                                {
                                    "text": self.description if self.description else "",
                                    "type": "text"
                                }
                            ],
                            "type": "paragraph"
                        }
                    ],
                    "type": "doc",
                    "version": 1
                },
                "issuetype": {
                    "id": config.key_issue_type
                },
                "project": {
                    "id": config.project_key
                },
                "labels": config.labels if config.labels else [],
                "summary": self.summary
            },
            "update": {},
        }
        if self.miror is not None:
            issue['fields'][config.s1_id_in_jira] = str(self.miror.id)
        return issue

    @staticmethod
    def convertir_json_en_issue(issue_json):
        try:
            issue_key = issue_json.get('key', None)
            issue_summary = issue_json['fields'].get('summary', None)
            description_data = issue_json['fields'].get('description', None)

            description_text = None
            if description_data is not None and 'content' in description_data:
                content_list = description_data['content']

                if content_list and content_list[0].get('content'):
                    description_text = content_list[0]['content'][0].get('text', None)

            issue_updated = issue_json['fields'].get('updated', None)
            status = issue_json['fields']['status']['name']
            status_updated = issue_json['fields'].get('statuscategorychangedate', None)
            return IssueS2(key=issue_key, summary=issue_summary, description=description_text,
                                         updated=issue_updated, status_updated=status_updated,
                                         status=status)
        except Exception as e:
            print(e)
            return None

    @classmethod
    def create_issue_lite(cls, issue_json):
        issue = IssueS2()
        issue.key = issue_json['key']
        issue.updated = issue_json['updated']
        return issue

    @staticmethod
    def get_miror(self):
        response = IssueS2.jira_request("GET", config.jira_url_ticket + self.key)
        if response.status_code == 200:
            mirror_id = response.json()['fields'].get(config.s1_id_in_jira, None)
            miror = IssueS1.find_by_id(mirror_id)
            return miror

    def get(self):
        try:
            response = IssueS2.jira_request("GET", config.jira_url_ticket + self.key)
            json_data = response.json()
            issue = IssueS2.convertir_json_en_issue(json_data)
            if issue is not None:
                return IssueS2(key=issue.key, summary=issue.summary, description=issue.description,
                                             status_updated=issue.status,
                                             updated=issue.updated, status=issue.status)
        except Exception as e:
            return e

    @staticmethod
    def jira_request(method, url, auth=config.auth, headers={}, params={}, data=None):
        try:
            response = requests.request(method, url, auth=auth, headers=headers, params=params, json=data,
                                        verify=config.verify_ssl_certificate)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            return response
        except requests.RequestException as e:
            return f"Erreur lors de la requête HTTP : {str(e)}"

    @staticmethod
    def find_by_id(key):
        try:
            # response = requests.request("GET", config.jira_url_ticket + key, headers={}, auth=config.auth)
            response = IssueS2.jira_request(method='get', url=config.jira_url_ticket + key)
            json_data = response.json()
            issue = IssueS2.convertir_json_en_issue(json_data)
            if issue is not None:
                return IssueS2(key=issue.key, summary=issue.summary, description=issue.description,
                                             updated=issue.updated, status=issue.status)
        except Exception as e:
            return e

    @staticmethod
    def find_by(jql_query):
        return IssueS2.get_issue_list_from_jira(jql_query=jql_query)
        # payload = {"jql": jql_query}
        # response = IssueS2.jira_request(method='get', url=config.jira_url_all, params=payload)
        # if response.status_code == 200:
        #     return response.json().get("issues", [])
        # else:
        #     return []

    # @staticmethod
    # def delete_all(jql_query):
    #     payload = {"jql": jql_query}
    #     response = requests.get(configurations.jira_url_all, params=payload, headers=configurations.headers, auth=configurations.auth)
    #     if response.status_code == 200:
    #         issues = response.json().get("issues", [])
    #         for issue in issues:
    #             IssueS2.delete(issue["key"])
    #     else:
    #         return f"Failed to execute search query. Status code: {response.status_code}"

    @staticmethod
    def get_jira_transitions_and_columns(issue_key):  #
        # # by description
        # description = 'voyons voir'
        # jql_query = f" description ~ {description} "
        # assert issues
        # assert issues[0]["key"] == key
        # assert description in issues[0]["fields"]["description"]["content"][0]["content"][0]["text"]
        #
        # # by champ detourné
        # s1_id = 6
        # jql_query = f" s1_id = {s1_id} "
        # assert issues
        # assert issues[0]["fields"][config.s1_id_in_jira] == str(s1_id)
        # assert issues[0]["key"] == key
        #
        # # by updated
        # updated = "2012-01-14 12:00"  # '2023-01-11T09:33:44.695+0100'
        # jql_query = f"updated >= {updated}"
        # issues = IssueS2.find_by(jql_query)
        # assert len(issues) == 0
        # # print(issues)

        # transitions methode 2
        transitions_url = f"{config.jira_url_base}/rest/api/2/issue/createmeta"
        # workflow_url = f"{configurations.jira_url_base}rest/api/2/workflow"
        # print("workflow url ",workflow_url)
        # #  la liste des workflows
        # workflows_response = requests.get(workflow_url, auth=configurations.auth)
        # print("repose",workflows_response)
        # workflows_data = workflows_response.json()
        # # on veux  les colonnes du premier workflow trouvé
        # if len(workflows_data) > 0:
        #     for work in workflows_data:
        #         print("work ...",work)
        #         if work["name"] == configurations.workflow_name:
        #             workflow_id = work["scope"]["project"]["id"]
        #             workflow_columns_url = f"{configurations.jira_url_base}rest/api/2/workflow/{workflow_id}/properties/jira.meta.statuses" #/properties/jira.meta.statuses
        #             print("workflow columnnn url ",workflow_columns_url)
        #             #  colonnes du workflow
        #             columns_response = requests.get(workflow_columns_url, auth=configurations.auth)
        #             print(columns_response)
        #             #columns_data = columns_response.json()
        #             #columns = [status['name'] for status in columns_data]
        #         else:
        #             columns = []
        return [], []

    @staticmethod
    def get_jira_transitions(issue_key):
        transitions = []
        transition_url = config.jira_url_ticket + issue_key + "/transitions"
        # transitions_response = requests.get(transition_url, auth=config.auth)
        response = IssueS2.jira_request(method='get', url=transition_url)
        transitions_data = response.json()
        transitions = [transition['name'] for transition in transitions_data['transitions']]
        return transitions

    @staticmethod
    def get_jira_status(projectIdOrKey='KAN'):
        status_url = f"{config.jira_url_base}/rest/api/3/project/{projectIdOrKey}/statuses"
        response = IssueS2.jira_request(method='get', url=status_url)
        if response.status_code == 200:
            json_data = response.json()[0]
            status_names = set()
            for status in json_data["statuses"]:
                status_names.add(status["name"])
            return status_names
        else:
            return response.status_code

    @staticmethod
    def length():
        issues = IssueS2.all()
        return len(issues)

    @staticmethod
    def all():
        return IssueS2.find_by(config.jql_query)

    @staticmethod
    def all_lite():
        fields = ['updated', 'statuscategorychangedate']
        issues = IssueS2.get_issue_list_from_jira(fields)
        return [IssueS2(key=issue["key"], updated=issue["fields"].get("updated", None),
                                      status_updated=issue["fields"].get("statuscategorychangedate")) for issue in
                issues]

    @staticmethod
    def all_weight():
        fields = ["updated", 'statuscategorychangedate', 'summary', 'description']
        issues = IssueS2.get_issue_list_from_jira(fields)
        return [IssueS2.convertir_json_en_issue(issue) for issue in issues]

    # take a list of fiels as parameter : fiels you wwant to get in the response
    @staticmethod
    def get_issue_list_from_jira(fields='', jql_query=''):
        batch_size = 100
        issues = []
        start_at = 0
        while True:
            params = {'jql': jql_query, "startAt": start_at, "maxResults": batch_size, "fields": fields,
                      "expand": 'changelog'}
            response = IssueS2.jira_request(method='get', url=config.jira_url_all, params=params)
            if response.status_code == 200:
                batch_tickets = response.json()["issues"]
                issues.extend(batch_tickets)
                start_at += batch_size
                if len(batch_tickets) < batch_size:
                    break  # on arrete la boucle si moins de tickets sont retournés que le batch_size
            else:
                return []
        return issues

    @staticmethod
    def get_project_list():
        project_url = f'{config.jira_url_base}/rest/api/3/project'
        response = IssueS2.jira_request(method='get', url=project_url)
        if response.status_code == 200:
            projects = response.json()

            for project in projects:
                print(project)
                print(project['key'], '-', project['name'], '-', project['id'])
            return [[project['key'], project['name'], project['id']] for project in projects]
        else:
            print(f"La requête a échoué avec le code d'erreur {response.status_code}")

    def save(self):
        response = IssueS2.jira_request(method='POST', url=config.jira_url_ticket,
                                                      data=self.format_issue_into_json())

        if response.status_code == 201:
            # return (json.loads(response.text)).get("key")
            return response
        else:
            return f"Erreur lors de la création du ticket. Code d'erreur : {response.status_code}"

    # def delete(self):
    #     response = requests.request("DELETE", config.jira_url_ticket + self.key, auth=config.auth)
    #
    #     if response.status_code == 204:
    #         print(f"Suppression effectuée avec succées")
    #     else:
    #         print(f"Erreur lors de la suppression du ticket. Code d'erreur : {response.status_code}")

    def update(self):
        response = IssueS2.jira_request(method='put', url=config.jira_url_ticket + self.key,
                                                      data=self.format_issue_into_json())
        return response.text

    # takes transitions as argument not status Name (Columns)
    def change_issue_status(self, new_status):
        transition_url = config.jira_url_ticket + self.key + "/transitions"
        # response = requests.get(transition_url, auth=config.auth)
        response = IssueS2.jira_request(method='get', url=transition_url)
        transitions = response.json()['transitions']
        transition_id = None
        for transition in transitions:
            if transition['name'] == new_status:
                transition_id = transition['id']
                break
        if not transition_id:
            return None

        data = {
            "transition": {"id": transition_id}
        }
        headers = {'Content-Type': 'application/json'}

        response = requests.post(transition_url, json=data, headers=headers, auth=config.auth)

        if response.status_code == 204:
            return transition_id
        else:
            print("Erreur lors du changement de statut:", response.text)
            return None

    # @staticmethod
    # def supprimer_tickets_entre_a_and_b(a, b):
    #     for i in range(a, b):
    #         key = "KAN-" + str(i)
    #         issue_to_delete = IssueS2(key=key, summary="", description="", updated="", status="")
    #         issue_to_delete.delete()

    @staticmethod
    def check_connection(jira_url=config.jira_url_base, username=config.username, api_token=config.api_token):
        try:
            auth = HTTPBasicAuth(username, api_token)
            response = requests.head(jira_url, auth=auth)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.RequestException as e:
            print("Erreur de connexion à Jira:", e)
            return False

    @staticmethod
    def create_isssue_and_move_to_done_for_performance_test(a, b):
        new_status = 'Terminé'
        status = "Pret"
        key_list = []
        for i in range(a, b):
            description = f'description_{i}'
            summary = f'summary_{i}'
            issue = IssueS2(summary=summary, description=description)
            key = issue.save()
            print(key)
            # key_list.append(key)
            # issue = IssueS2.find_by_id(key)
            # result = issue.change_issue_status(new_status)
            # print(f'transition id {result}   key {key}  iteration {i}')
            # issue.delete()
            # break
        # print(key_list)
        # return key_list

    @staticmethod
    def create_issues(a, b):
        for i in range(a, b):
            description = f'description_{i}'
            summary = f'summary_{i}'
            issue = IssueS2(summary=summary, description=description)
            key = issue.save()
            print(key)

    @staticmethod
    def all_key():
        fields = ["updated"]
        return [issue.get('key') for issue in IssueS2.get_issue_list_from_jira(fields)]

    @staticmethod
    def save_data_json_in_file():
        all_tickets = IssueS2.get_issue_list_from_jira()
        IssueS2.save_json_file(config.json_issues_file,all_tickets)


    @staticmethod
    def save_json_file(file_name,data):
        with open(file_name, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return True