def config_package():
    with open('config.py', 'w') as fichier_config:
        fichier_config.write(f"""import logging
import os
from requests.auth import HTTPBasicAuth \n

username = "BillGates" 
#Api token de jira 
api_token = "TATT3xFfGF0nqgTV-RGN17B9CmizmQD0Mmr5ZY-pU0t8TjTzz0lyX0MNJ0XoNdKNy_t4eq9Is3Gw51Mta-kHF0XrEjKUANWzJM1XpRqS_-wSssC"
jira_url_base = "https://example.atlassian.net/"
jira_url_all = jira_url_base + "rest/api/3/search"
jira_url_ticket = jira_url_base + "rest/api/3/issue/"
verify_ssl_certificate = False

project_key = "90009"
key_issue_type = "10005"
s1_id_in_jira = "customfield_10054"

statusesS1 = ["status1", "status2", "status3", "status4"]
jiraStatusName = ['Pret', 'En attente', 'en cours', 'Qualifications']

module_to_use = "synch2jira.issue_S3"
class_to_use = "IssueS3"
                             
jql_query = 'project = KAN'

rate_column = 'Qualifications'

auth = HTTPBasicAuth(username, api_token)
main_directory = os.path.dirname(os.path.abspath(__file__))
config_file = main_directory + "/config.py"
workflow_database_file = "sqlite:///" + main_directory + "/database/worflow_bd.db"
csv_file = main_directory + "/csv_file.csv"
time_to_sleep = 0.1
""")


def config_database_workflow():
    from synch2jira.issue_wokflow import IssueWokflow
    IssueWokflow.fill_issue_workflow_bdd()
