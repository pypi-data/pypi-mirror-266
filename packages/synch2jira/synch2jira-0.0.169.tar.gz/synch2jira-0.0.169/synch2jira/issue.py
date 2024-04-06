from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional
import config
import csv
from synch2jira.issue_workflow import WorkFlow


@dataclass
class Issue:
    summary: str
    description: str
    updated: date
    status: str
    status_updated: date
    miror: Optional[Issue] = None

    issue_key :str
    issue_id : str
    statuscategorychangedate : str
    issuetypeid : str
    issuetypedescription : str
    issuetypename : str 
    issuetypesubtask : bool
    issuetypehierarchyLevel : str 
    timespend : str   
    projectid : str 
    projectkey : str 
    projectname : str
    projectTypeKey : str 
    aggregatetimespent : str 
    resolution : str 
    resolutiondate : str 
    workratio : str 
    watchCount : str 
    isWatching : bool
    lastViewed : str
    created : str
    priorityname : str 
    priorityid : str 
    labelsnumber : str 
    assignee : str 
    #updated : str
    statusname : str 
    statuscategoryname : str 
    timeoriginalestimate : str
    #description : str 
    security : str 
    aggregatetimeestimate : str
    #summary : str 
    creatoremailAddress : str 
    creatorname : str
    subtasksnumber : str 
    reportername : str 
    reporteremail : str 
    duedate : str
    votes : str 
    lead_time : str



    def json_to_issue(json_data):
        fields = json_data.get("fields", {})
        return Issue(
    issue_key=json_data.get("key"),
    issue_id=json_data.get("id"),
    statuscategorychangedate=fields.get("statuscategorychangedate"),
    issuetypeid=fields["issuetype"].get("id"),
    issuetypedescription=fields["issuetype"].get("description"),
    issuetypename=fields["issuetype"].get("name"),
    issuetypesubtask=fields["issuetype"].get("subtask"),
    issuetypehierarchyLevel=fields["issuetype"].get("hierarchyLevel"),
    timespend=fields.get("timespent"),
    projectid=fields["project"].get("id"),
    projectkey=fields["project"].get("key"),
    projectname=fields["project"].get("name"),
    projectTypeKey=fields["project"].get("projectTypeKey"),
    aggregatetimespent=fields.get("aggregatetimespent"),
    resolution=fields.get("resolution"),
    resolutiondate=fields.get("resolutiondate"),
    workratio=fields.get("workratio"),
    watchCount=fields["watches"].get("watchCount"),
    isWatching=fields["watches"].get("isWatching"),
    lastViewed=fields.get("lastViewed"),
    created=fields["created"].replace(" ", ""),
    priorityname=fields["priority"].get("name"),
    priorityid=fields["priority"].get("id"),
    labelsnumber=len(fields.get("labels", [])),
    assignee=fields.get("assignee"),
    updated=fields["updated"].replace(" ", ""),
    statusname=fields["status"].get("name"),
    statuscategoryname=fields["status"]["statusCategory"].get("name"),
    timeoriginalestimate=fields.get("timeoriginalestimate"),
    description="",
    #description=fields["description"]["content"][0].get("text"),
    security=fields.get("security"),
    aggregatetimeestimate=fields.get("aggregatetimeestimate"),
    summary=fields.get("summary"),
    creatoremailAddress=fields["creator"].get("emailAddress"),
    creatorname=fields["creator"].get("displayName"),
    subtasksnumber=len(fields.get("subtasks", [])),
    reportername=fields["reporter"].get("displayName"),
    reporteremail=fields["reporter"].get("emailAddress"),
    duedate=fields.get("duedate", ""),
    votes=fields["votes"].get("votes"),
    lead_time=WorkFlow.get_duration_between_two_state(json_data.get("key"),"","")
)

    def generate_csv_data(issue_list, file_path):
        fieldnames = Issue.__annotations__.keys()

        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for issue in issue_list:
                issue_dict = issue.__dict__
                writer.writerow(issue_dict)

    def delete(self):
        pass

    def get(self):
        pass

    def all(self):
        pass

    def update(self):
        pass

    def synchroniser_status_miroir_avec_status(self):
        if self.miror:
            print(self.miror.status)
            self.miror.status = config.status_dict_S2_to_S1[self.status]
            self.miror.update()
            return True
        return False

    @classmethod
    def convertirS_enS_(cls, issue):
        return cls(summary=issue.summary, description=issue.description, status=issue.status, updated=datetime.now())

    @staticmethod
    def convertir_en_format_date(date_to_convert):
        if isinstance(date_to_convert, datetime):
            date_to_convert = date_to_convert.strftime('%Y-%m-%d %H:%M:%S.%f')
        date = datetime.strptime(date_to_convert, '%Y-%m-%d %H:%M:%S.%f')
        offset = date.utcoffset()
        date_formattee = date + (offset if offset else timedelta(hours=0))
        return date_formattee

    @staticmethod
    def convertir_str_date_en_datetime(date_to_convert):
        date_without_timezone = date_to_convert[:-5]
        date_without_microseconds = datetime.strptime(date_without_timezone, '%Y-%m-%dT%H:%M:%S.%f')
        microseconds = int(date_to_convert[-5:])
        return date_without_microseconds.replace(microsecond=microseconds)

    @classmethod
    def all_attribut_id_et_updated(cls):
        issues = cls.all_filtre_id_et_updated()
        issues_list = []
        for issue in issues:
            issues_list.append(cls(summary="", description="", updated=issue.updated, status=""))
        return issues_list

    @staticmethod
    def date_S1_entre_date_derniere_synchro_et_date_S2(date_S1, date_S2):
        last_synchronized_date = Issue.convertir_str_date_en_datetime(config.last_synchronized_data_in_S2)
        date_S1_format_datetime = Issue.convertir_en_format_date(date_S1)
        date_S2_format_datetime = Issue.convertir_str_date_en_datetime(date_S2)

        return last_synchronized_date <= date_S1_format_datetime < date_S2_format_datetime

    def synch_summary(self):
        if self.miror:
            print(self.miror.summary)
            self.summary = self.miror.summary
            self.update()
            return True
        return False

    def synch_description(self):
        if self.miror:
            self.description = self.miror.description
            self.update()
            return True
        return False

    def synch_status(self):
        if self.miror:
            try:
                self.change_issue_status(config.status_dict_S1_to_S2[self.miror.status])
                return True
            except Exception as e:
                try:
                    self.change_issue_status(config.status_dict_S2_to_S1[self.miror.status])
                    return True
                except Exception as e:
                    return False

    def synchroniser_status_avec_status_miroir(self):
        if self.miror:
            print(self.miror)
            self.change_issue_status(config.status_dict_S1_to_S2[self.miror.status])
            return True
        return False

    def synchroniser_status_miroir_status(self):
        if self.miror:
            print(self.miror.status)
            self.miror.status = config.status_dict_S2_to_S1[self.status]
            self.miror.update()
            return True
        return False

    def synch_summary_from_miror(self):
        self.summary = self.miror.summary
        # Il faut juste qu'il update summary et non pas description aussi et tout !
        self.update()

    def synch_summary_to_miror(self):
        self.miror.summary = self.summary
        self.update()

    def synch_description_from_miror(self):
        self.description = self.miror.description
        self.update()

    def synch_description_to_miror(self):
        self.miror.description = self.description
        self.update()

    @staticmethod
    def issue1_factory(summary, description, updated, status):
        module_name = config.module_to_use
        class_name = config.class_to_use
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        return cls(summary, description, updated, status)

    def get_workflow_duration_between_to_status(self, status1, status2):
        for history in self.workflow_history:
            if history["to_state"] == status1:
                begin = history["status_change_time"]
            if history["to_state"] == status2:
                end = history["status_change_time"]
        return begin, end
