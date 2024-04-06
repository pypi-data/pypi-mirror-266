import csv
from synch2jira.issue import Issue

class IssueCSV():
     
    @staticmethod
    def generate_csv_data(issue_list, file_path):
            fieldnames = Issue.__annotations__.keys()
            print(fieldnames)

            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for issue in issue_list:
                    issue_dict = issue.__dict__
                    writer.writerow(issue_dict)