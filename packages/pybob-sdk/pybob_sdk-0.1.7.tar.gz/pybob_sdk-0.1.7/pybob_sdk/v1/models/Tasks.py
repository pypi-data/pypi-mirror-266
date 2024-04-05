from pydantic import BaseModel
from typing import Optional


class Owner(BaseModel):
    id: str
    firstName: str
    surname: str
    email: str
    displayName: str


class Task(BaseModel):
    id: int
    owner: Owner
    title: str
    requestedFor: Owner
    due: str
    linkInBob: Optional[str]
    set: str
    workflow: str
    ordinalInWorkflow: int
    description: Optional[str]
    status: str
    completionDate: Optional[str]
    employeeGroupId: Optional[str]
    companyId: int
