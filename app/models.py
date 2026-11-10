from pydantic import BaseModel, Field
from typing import Literal, Optional

Action = Literal["DELETE", "ANONYMIZE"]

class RTBFRequestIn(BaseModel):
    subject_type: Literal["EMAIL", "CUSTOMER_ID"] = "EMAIL"
    subject_value: str = Field(min_length=3)
    action: Action = "DELETE"
    jurisdiction: str = "GDPR"
    reason: str = "Customer request"

class IngestionCheck(BaseModel):
    subject_value: str

class RTBFResponse(BaseModel):
    request_id: str
    status: str
    action: str
    exclusion_created: bool

class SystemActionResult(BaseModel):
    system: str
    action: str
    outcome: str
    record_ref: Optional[str] = None
    detail: str = ""
