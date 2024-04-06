from pydantic import BaseModel, validator, ValidationError, Field
from typing import Set, Optional
import uuid
from datetime import datetime
from . import pulse_enums as enums
import dateutil.parser

CLASS_VERSION= 1.0
MODULE= "core"
CLASS_REF="orgn"


class Organisation(BaseModel):
    puid: str = Field(default_factory=lambda: f"{datetime.utcnow().strftime('%Y%m%d%H%M')}{uuid.uuid4().hex[:8]}_{MODULE}{CLASS_REF}".lower())
    name: str
    creat_date: datetime = Field(default_factory=lambda:datetime.utcnow()) 
    updt_date: datetime = Field(default_factory=lambda:datetime.utcnow())
    creat_by_user: Optional[str] = None  
    updt_by_user: Optional[str] = None 
    relations: Optional[Set[str]]=None
    description: Optional[str] = None  # Updated to use Optional
    industries: Optional[Set[str]] = None  # Updated to use Optional
    website: Optional[str] = None  # Updated to use Optional
    org_admin_user_uids: Optional[Set[str]] = None  # Updated to use Optional
    class Config:
            extra = "forbid"


    @validator('relations', pre=True, always=True)
    def validate_relations(cls, relations):
        if not set(relations).issubset(enums.organisation_relations):
            raise ValueError("Invalid relation values provided.")
        return relations

   
    @validator('industries', pre=True, always=True)
    def validate_industries(cls, industries):
        if industries is not None and not set(industries).issubset(enums.organisation_industries):
            raise ValueError("Invalid industry values provided.")
        return industries
    
    @validator('creat_date', 'updt_date', pre=True)
    def parse_date(cls, value):
        if value is None:
            return value
        if isinstance(value, datetime):
            return value
        try:
            # Assuming Firestore returns an ISO 8601 string, adjust if necessary
            print("Putting Updt or Creat date in a valid format in a Validator when creating Organisation object")
            return dateutil.parser.isoparse(value)
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid datetime format inside Organisation: {value}")


    ### Description, Industries, and Website are optional for Retail Customer and mandatory for Non Retail Customer
    @validator('description', 'industries', 'website', pre=True, always=True)
    def validate_optional_fields(cls, value, values):
        if values.get('name') == 'Retail Customer' and values.get('relations') == {"retail_customer"} or  values.get('relations') == ["retail_customer"]:
            if value is not None:
                raise ValueError("For 'Retail Customer' with only 'retail_customer' relations, description, industries, and website should not be provided.")
        else:
            if value is None:
                raise ValueError("For Non Retail Customer, description, industries, and website are mandatory.")
        return value