from typing import Optional, Set
from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime


CLASS_ORIGIN_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_ORGIN_DATE=datetime(2024, 3, 15, 20, 15)

CLASS_VERSION = 2.01
CLASS_REVISION_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_REVISION_DATE=datetime(2024, 3, 15, 20, 15)
LAST_MODIFICATION="Created , with all fields Optional"

class UserProfileUpdate(BaseModel):
    schema_version: Optional[float] = Field(None, description="Version of this Class == version of DB Schema")
    email: Optional[EmailStr] = Field(None, description="Propagated from Firebase Auth")
    organizations_uids: Optional[Set[str]] = Field(None, description="Depends on Subscription Plan, Regularly Updated")
    creat_date: Optional[datetime] = Field(None, description="Creation date")
    creat_by_user: Optional[str] = Field(None, description="Created by user")
    updt_date: Optional[datetime] = Field(None, description="Update date")
    updt_by_user: Optional[str] = Field(None, description="Updated by user")
    aliases: Optional[Set[str]] = Field(None, description="User aliases")
    provider_id: Optional[str] = Field(None, description="Provider ID")

    username: Optional[str] = Field(None, description="Username")
    dob: Optional[date] = Field(None, description="Date of Birth")
    first_name: Optional[str] = Field(None, description="First Name")
    last_name: Optional[str] = Field(None, description="Last Name")
    mobile: Optional[str] = Field(None, description="Mobile Number")
    
    # def model_dump(self, **kwargs):
    #         return super().model_dump(exclude_none=True, **kwargs)
        
        
        
        