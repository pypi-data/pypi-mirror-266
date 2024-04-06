from dataclasses import dataclass

from synch2jira.issue import Issue
from synch2jira.issue_wokflow_json import IssueWokflowJSON


@dataclass 
class  IssueJSON(Issue):
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
    updated : str
    statusname : str 
    statuscategoryname : str 
    timeoriginalestimate : str
    description : str 
    security : str 
    aggregatetimeestimate : str
    summary : str 
    creatoremailAddress : str 
    creatorname : str
    subtasksnumber : str 
    reportername : str 
    reporteremail : str 
    duedate : str
    votes : str 
    workflow_start_time : str
    workflow_end_time : str

    @staticmethod
    def json_to_issue(issue_data,json_data):
        print(f'type {type(issue_data)}')
        fields = issue_data.get("fields", {})
        issue_key=issue_data.get("key")
        workflow_end_time,workflow_start_time = IssueWokflowJSON.get_lead_time(json_data,issue_key,'en cours','Qualifications')
        return IssueJSON(
    issue_key=issue_data.get("key"),
    issue_id=issue_data.get("id"),
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
    workflow_start_time=workflow_start_time,
    workflow_end_time=workflow_end_time
   
)