from pydantic import BaseModel, EmailStr , Field
from datetime import datetime , date

from typing import Set, Optional
# import uuid
# from . import pulse_enums as enums

CLASS_ORIGIN_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_ORGIN_DATE=datetime(2024, 1, 16, 20, 5)

CLASS_VERSION = 3.01
CLASS_REVISION_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_REVISION_DATE=datetime(2024, 2, 13, 20, 15)
LAST_MODIFICATION="Fixed typo"


DOMAIN="user"
OBJ_REF = "usprfl"

class UserProfile(BaseModel):
    schema_version: float = Field(default=CLASS_VERSION, description="Version of this Class == version of DB Schema") #User can Read only
    # uid: str = Field(frozen=True, description="Combination of user_usrprof_<Firebase Auth UID>") #User can Read only ---> STORED as Firestore Doc ID
    # puid:str = Field(default_factory=lambda: f"{DOMAIN}{OBJ_REF}{datetime.utcnow().strftime('%Y%m%d%H%M')}{uuid.uuid4().hex[:8]}".lower(),
    #                   frozen=True, 
    #                   description="Generated Automatically by default_factory") #User can Read only
    email: EmailStr =  Field(frozen=True, description="Propagated from Firebase Auth" ) #User can Read only
    organizations_uids: Set[str] = Field( description="Depends on Subscription Plan, Regularly Updated") #User can Read only  
    creat_date: datetime #User can Read only
    creat_by_user: str #User can Read only
    updt_date: datetime #User can Read only
    updt_by_user: str #User can Read only
    aliases: Optional[Set[str]] = None #User can Read only
    provider_id: str   #User can Read only
    
    username: Optional[str] = None #User can Read and Edit
    dob: Optional[date] = None #User can Read and Edit 
    first_name: Optional[str] = None #User can Read and Edit 
    last_name: Optional[str] = None #User can Read and Edit 
    mobile: Optional[str] = None #User can Read and Edit
    class Config:
        extra = "forbid"