import csv
from dataclasses import dataclass
from datetime import datetime, timezone


import config
from synch2jira.issue_S2 import IssueS2




@dataclass
class IssueWokflowJSON():
   
    def __init__(self, issueKey, status, updated, from_time, to_time):
        self.from_time = from_time
        self.issueKey = issueKey
        self.updated = updated
        self.status = status
        self.to_time = to_time

   
    @staticmethod
    def get_issue_from_json(issue_key, json_data):
        for issue in json_data : 
            if issue.get('key') == issue_key:
                return issue
        return 

    def get_workflow(json_data,issue_key,status):
        issue_data = IssueWokflowJSON.get_issue_from_json(issue_key,json_data)
        changelog = issue_data.get("changelog", [])
        histories = changelog.get("histories", [])
        from_time = []
        to_time = []
        for history in histories:
            created = history.get("created", [])
            print(created)
            items = history.get('items', [])
            for item in items:
                field = item['field']
                if field == "status":
                    #if item['fromString'] == status:
                        #from_time.append(created)
                    if item['toString'] == status:
                        to_time.append(created)
                min_from_time = None if from_time == [] else min(from_time)
        max_to_time = None if to_time == [] else max(to_time)
        print(to_time,max_to_time)
        return max_to_time
    
    @staticmethod
    def get_lead_time(json_data,issue_key, first_status, last_status):
        workflow1 = IssueWokflowJSON.get_workflow(json_data, issue_key,first_status)
        workflow2 = IssueWokflowJSON.get_workflow(json_data, issue_key,last_status)
        print(workflow1,workflow2)
        return workflow1,workflow2


    @staticmethod
    def save_result_in_csv(result, entete):
        filename = config.csv_file
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(entete)
            for row in result:
                writer.writerow(row)
        print(f"Les données ont été écrites dans {filename}")

   