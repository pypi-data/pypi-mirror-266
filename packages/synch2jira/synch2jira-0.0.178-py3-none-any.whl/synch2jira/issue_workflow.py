import csv
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, create_engine, DateTime, and_, text, desc
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base

import config
from synch2jira.log import new_log
from synch2jira.issue_S2 import IssueS2

Base = declarative_base()
engine = create_engine(config.workflow_database_file)
Session = sessionmaker(bind=engine)
session = Session()


@dataclass
class IssueWorkflow(Base):
    __tablename__ = 'issue_worflow'
    id = Column(Integer, autoincrement=True, primary_key=True)
    issueKey = Column(String)
    status = Column(String)
    updated = Column(DateTime)
    from_time = Column(String)
    to_time = Column(String)

    def __init__(self, issueKey, status, updated, from_time, to_time):
        self.from_time = from_time
        self.issueKey = issueKey
        self.updated = updated
        self.status = status
        self.to_time = to_time

    @staticmethod
    def get_workflow_history(self):
        return self.all()

    @staticmethod
    def update_last_updated(issue_key, updated):
        issue = IssueWorkflow.find_by_id(issue_key)
        issue.updated = updated
        issue.update()

        return None

    @staticmethod
    def fill_issue_workflow_bdd():
        try : 
            IssueWorkflow.create_all_tables()
            #IssueWorkflow.delete_all()
            IssueWorkflow.get_workflow()
        except Exception as e :
            new_log("ERROR",f"Erreur lors du remplissage de la base de données : {str(e)}")

    @staticmethod
    def save_issue_workflow(issue_key):
        try:
            jira_transitions = config.jiraStatusName
            for status in jira_transitions:
                from_time, to_time = IssueWorkflow.get_workflow(issue_key, status)  # 691ms
                workflow = IssueWorkflow(issue_key, status, datetime.now(), from_time, to_time)
                workflow.save()  # 7ms
        except Exception as e:
            new_log("ERROR",f"Erreur lors de la sauvegarde du workflow de l'issue {issue_key} : {str(e)}")

    @staticmethod
    def did_issue_have_state(issue_key, state):
        workflow_list = IssueWorkflow.find_by(issueKey=issue_key, status=state)
        for workflow in workflow_list:
            if workflow.to_time:
                return True
        return False

    @staticmethod
    def synchronize_data_with_jira():
        print('calling synch')
        jira_columns = config.jiraStatusName
        issue_in_jira_list = IssueS2.all_lite()
        workflow_list = IssueWorkflow.all_keys()
        for issue_jira in issue_in_jira_list:
            if issue_jira.key not in workflow_list:
                IssueWorkflow.save_issue_workflow(issue_jira.key)
            else:
                print(IssueWorkflow.find_by_id(issue_jira.key))
                workflow = IssueWorkflow.find_by_id(issue_jira.key)[0]
                print(issue_jira.key, workflow.updated, issue_jira.status_updated)
                # print(type(workflow.updated),type(issue_jira.updated))
                is_updated_on_date = IssueWorkflow.compare_str_dates(workflow.updated, issue_jira.status_updated)
                if not is_updated_on_date:
                    for status in jira_columns:
                        from_time, to_time = IssueWorkflow.get_workflow(issue_jira.key, status)
                        workflow = IssueWorkflow.find_by(issueKey=issue_jira.key, status=status)[0]
                        workflow.from_time = from_time
                        workflow.to_time = to_time
                        workflow.update()
                        print(workflow.issueKey)
                    # workflow.save()

    @staticmethod
    def compare_str_dates(date1, date2):
        date1 = date1.replace(tzinfo=timezone.utc)
        date2 = datetime.strptime(date2, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=timezone.utc)
        print(f'date 1 {date1} , date 2 {date2}')
        if date1 > date2:
            # KAN-17 2024-03-05 09:13:40.998417 2024-03-05T11:27:28.959+0100
            # KAN-99 2024-03-05 11:06:19.485890 2024-03-05T11:27:29.733+0100
            return True

        return False

    @staticmethod
    def get_workflow():
        from_time = []
        to_time = []
        workflows = []
        #issues = IssueS2.get_issue_data_from_jira()
        issues = IssueS2.get_issue_data_from_jira()
        try : 
            for issue in issues:
                issue_key = issue["key"]
                changelog = issue.get("changelog", {})
                histories = changelog.get("histories", [])
                for stat in config.jiraStatusName:
                    for history in histories:
                        created = history.get("created", "")
                        items = history.get('items', [])
                        for item in items:
                            field = item['field']
                            if field == "status":
                                if item['fromString'] == stat:
                                    from_time.append(created)
                                if item['toString'] == stat:
                                    to_time.append(created)
                    min_from_time = None if from_time == [] else min(from_time)
                    max_to_time = None if to_time == [] else max(to_time)
                    workflow = IssueWorkflow(issue_key, stat, datetime.now(), min_from_time, max_to_time)
                    workflows.append(workflow)
        except Exception as e: 
            new_log("ERROR",f"Erreur lor du parsage dans la fonction get_workflow : {str(e)}")
        IssueWorkflow.save_all(workflows)

    def get_workflow_():
        pass

    @staticmethod
    def save_result_in_csv(result, entete):
        try: 
            filename = config.csv_file
            with open(filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(entete)
                for row in result:
                    writer.writerow(row)
            new_log("INFO",f"Les données ont été écrites dans {filename}")
        except Exception as e: 
            new_log("ERROR","Erreur lors de la creation du fichier workflow csv")

    @staticmethod
    def create(**kwargs):  # avec les argument on creee un objet et on le save
        workflow = IssueWorkflow(**kwargs)
        session.add(workflow)
        session.commit()
        return workflow

    @staticmethod
    def create_all_tables():
        try:
            Base.metadata.create_all(engine)
            return True
        except OperationalError:
            return new_log("ERROR","Les tables existent déjà.")
        except Exception as e:
            return new_log("ERROR",f"Une erreur s'est produite : {e}")

    @staticmethod
    def new(**kwargs):  # avec les argument on creee un objet sans le save
        return IssueWorkflow(**kwargs)

    @staticmethod
    def all():
        return session.query(IssueWorkflow).all()

    @staticmethod
    def all_keys():
        return list(set([workflow.issueKey for workflow in IssueWorkflow.all()]))

    @staticmethod
    def length():
        return len(IssueWorkflow.all())

    def save(self):
        session.add(self)
        session.commit()
        return self

    def get(self):
        return session.query(IssueWorkflow).filter(
            and_(IssueWorkflow.issueKey == self.issueKey, IssueWorkflow.status == self.status)).first()

    @staticmethod
    def first():
        return session.query(IssueWorkflow).first()

    @staticmethod
    def last():
        return session.query(IssueWorkflow).order_by(desc(IssueWorkflow.issueKey)).first()

    @staticmethod
    def find_by(**kwargs):
        return session.query(IssueWorkflow).filter_by(**kwargs).all()

    @staticmethod
    def find_by_id(key):
        return session.query(IssueWorkflow).filter_by(issueKey=key).all()

    @staticmethod
    def update(instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        session.commit()

    def update(self):
        self.updated = datetime.now()
        session.merge(self)
        session.commit()

    @staticmethod
    def update_all(**kwargs):
        session.query(IssueWorkflow).update(kwargs)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()

    @staticmethod
    def delete_all():
        session.execute(text("DELETE FROM issue_worflow"))
        session.commit()

    @staticmethod
    def save_all(liste):
        try:
            session.add_all(liste)
            session.commit()
        except Exception as e:
            new_log("ERROR",f" eErreur lors de la sauvegarde des workflow deans la BDD: {e}")
            session.rollback()
