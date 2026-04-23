# Create CSV files for the user in /mnt/data

import pandas as pd
from pathlib import Path

base_path = Path('services/user_access/data')
base_path.mkdir(exist_ok=True)

# Define datasets
datasets = {
    "users.csv": [
        ["U001","Dr. Alice Smith","alice.smith@pharma.com","Clinical","Clinical Scientist","active"],
        ["U002","Dr. Bob Lee","bob.lee@pharma.com","Biostatistics","Biostatistician","active"],
        ["U003","Carol Jones","carol.jones@pharma.com","Data Management","Data Manager","active"],
        ["U004","David Kim","david.kim@pharma.com","QA","QA Reviewer","active"],
        ["U005","Emma Brown","emma.brown@pharma.com","Regulatory","Regulatory Specialist","active"],
        ["U006","Frank Wilson","frank.wilson@pharma.com","IT","Platform Engineer","active"],
        ["U007","Grace Liu","grace.liu@pharma.com","Clinical","Clinical Scientist","active"],
        ["U008","Henry Patel","henry.patel@pharma.com","Biostatistics","Senior Biostatistician","active"],
        ["U009","Isha Verma","isha.verma@pharma.com","Data Privacy","Data Privacy Officer","active"],
        ["U010","John Carter","john.carter@pharma.com","External","External Collaborator","active"],
    ],
    "studies.csv": [
        ["STUDY001","Phase III Oncology Trial","Oncology","ongoing"],
        ["STUDY002","Diabetes Drug Study","Endocrinology","ongoing"],
        ["STUDY003","Cardiology Outcomes Study","Cardiology","completed"],
        ["STUDY004","Neurology Biomarker Study","Neurology","ongoing"],
        ["STUDY005","Immunotherapy Research Study","Immunology","planning"],
    ],
    "resources.csv": [
        ["RES001","Oncology Patient Dataset","dataset","STUDY001","HIGH","Clinical Ops"],
        ["RES002","Diabetes Analysis Dataset","dataset","STUDY002","MEDIUM","Data Science"],
        ["RES003","Cardiology Results Dataset","dataset","STUDY003","LOW","Clinical Ops"],
        ["RES004","Neurology Biomarker Dataset","dataset","STUDY004","HIGH","Research"],
        ["RES005","Immunotherapy Trial Dataset","dataset","STUDY005","MEDIUM","Clinical Ops"],
        ["RES006","Oncology Pipeline","pipeline","STUDY001","MEDIUM","Data Engineering"],
        ["RES007","Diabetes Reporting Dashboard","report","STUDY002","LOW","BI Team"],
        ["RES008","Cardiology Submission Report","report","STUDY003","MEDIUM","Regulatory"],
        ["RES009","Neurology Analysis Pipeline","pipeline","STUDY004","HIGH","Data Engineering"],
        ["RES010","Immunotherapy Dashboard","report","STUDY005","LOW","BI Team"],
    ],
    "roles.csv": [
        ["R001","Clinical Scientist","Access to clinical datasets and analysis"],
        ["R002","Biostatistician","Advanced statistical analysis permissions"],
        ["R003","Data Manager","Manage and curate datasets"],
        ["R004","QA Reviewer","Review and approve submissions"],
        ["R005","Regulatory Specialist","Finalize and submit reports"],
        ["R006","Platform Engineer","System-level access to pipelines"],
        ["R007","Data Privacy Officer","Access to highly sensitive patient data"],
    ],
    "permissions.csv": [
        ["P001","read","dataset"],
        ["P002","write","dataset"],
        ["P003","run","pipeline"],
        ["P004","read","report"],
        ["P005","approve","report"],
        ["P006","export","dataset"],
    ],
    "role_permissions.csv": [
        ["R001","P001"],["R001","P004"],
        ["R002","P001"],["R002","P003"],["R002","P006"],
        ["R003","P001"],["R003","P002"],
        ["R004","P004"],["R004","P005"],
        ["R005","P004"],["R005","P005"],
        ["R006","P003"],
        ["R007","P001"],["R007","P006"],
    ],
    "user_roles.csv": [
        ["U001","R001","study","STUDY001","2026-04-01T10:00:00Z"],
        ["U002","R002","study","STUDY001","2026-04-02T11:00:00Z"],
        ["U003","R003","study","STUDY002","2026-04-03T12:00:00Z"],
        ["U004","R004","study","STUDY001","2026-04-04T13:00:00Z"],
        ["U005","R005","study","STUDY003","2026-04-05T14:00:00Z"],
        ["U006","R006","study","STUDY001","2026-04-06T15:00:00Z"],
        ["U007","R001","study","STUDY004","2026-04-07T16:00:00Z"],
        ["U008","R002","study","STUDY003","2026-04-08T17:00:00Z"],
        ["U009","R007","study","STUDY001","2026-04-09T18:00:00Z"],
        ["U010","R001","study","STUDY002","2026-04-10T19:00:00Z"],
    ],
    "access_requests.csv": [
        ["REQ001","U001","RES002","read","study","STUDY002","Need cross-study analysis","PENDING","2026-04-20T09:00:00Z"],
        ["REQ002","U002","RES001","read","study","STUDY001","Statistical modeling","PENDING","2026-04-20T10:00:00Z"],
        ["REQ003","U003","RES001","write","study","STUDY001","Data correction needed","APPROVED","2026-04-19T11:00:00Z"],
        ["REQ004","U004","RES008","approve","study","STUDY003","QA validation","PENDING","2026-04-21T12:00:00Z"],
        ["REQ005","U005","RES008","approve","study","STUDY003","Regulatory submission","APPROVED","2026-04-18T13:00:00Z"],
        ["REQ006","U007","RES004","read","study","STUDY004","Biomarker analysis","PENDING","2026-04-22T14:00:00Z"],
        ["REQ007","U008","RES003","export","study","STUDY003","Final report generation","APPROVED","2026-04-17T15:00:00Z"],
        ["REQ008","U009","RES001","read","study","STUDY001","Privacy audit","PENDING","2026-04-22T16:00:00Z"],
        ["REQ009","U010","RES002","read","study","STUDY002","External collaboration","PENDING","2026-04-23T08:00:00Z"],
        ["REQ010","U001","RES006","run","study","STUDY001","Pipeline execution","PENDING","2026-04-23T09:30:00Z"],
    ],
    "access_decisions.csv": [
        ["DEC001","REQ003","U004","APPROVED","Valid data update","2026-04-19T12:00:00Z"],
        ["DEC002","REQ005","U005","APPROVED","Meets regulatory requirements","2026-04-18T14:00:00Z"],
        ["DEC003","REQ007","U004","APPROVED","Export approved for reporting","2026-04-17T16:00:00Z"],
    ]
}

# Column headers
headers = {
    "users.csv": ["user_id","name","email","department","title","status"],
    "studies.csv": ["study_id","study_name","therapeutic_area","status"],
    "resources.csv": ["resource_id","resource_name","resource_type","study_id","sensitivity","owner"],
    "roles.csv": ["role_id","role_name","description"],
    "permissions.csv": ["permission_id","action","resource_type"],
    "role_permissions.csv": ["role_id","permission_id"],
    "user_roles.csv": ["user_id","role_id","scope_type","scope_id","granted_at"],
    "access_requests.csv": ["request_id","user_id","resource_id","requested_action","scope_type","scope_id","justification","status","created_at"],
    "access_decisions.csv": ["decision_id","request_id","approver_id","decision","comments","decided_at"]
}

# Save files
file_paths = []
for filename, rows in datasets.items():
    df = pd.DataFrame(rows, columns=headers[filename])
    path = base_path / filename
    df.to_csv(path, index=False)
    file_paths.append(str(path))

file_paths