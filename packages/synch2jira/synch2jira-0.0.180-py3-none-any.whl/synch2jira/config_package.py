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
verify_ssl_certificate = True

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
workflow_file = main_directory + "/database/worflow_bd.db"
workflow_database_directory = main_directory + "/database/"
time_to_sleep = 0.1
files_directory = main_directory + "/files"
csv_file = main_directory + "/workflow_time.csv"
log_directory = main_directory + "/log/"                             
log_file = main_directory + "/log/file.log"
log_format = '%(asctime)s - %(levelname)s - %(message)s'
json_issues_file = main_directory + "/files/json_issues.json"
csv_issue_file = main_directory + "/files/json_issues.csv"                          


""")


def config_database_workflow():
    from synch2jira.issue_workflow import IssueWorkflow
    IssueWorkflow.fill_issue_workflow_bdd()
