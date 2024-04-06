import uuid
from datetime import datetime
from pydantic import BaseModel, validator, ValidationError
from typing import Dict, Any, Set, Optional
from . import pulse_enums as enums

import dateutil.parser

CLASS_VERSION = 1.0
CLASS_REF = "resdes"
MODULE = "core"

        # metadata = {
        #     "resr_puid_or_name":"Users",
        #     "resr_path":"firestore/Users",
        #     "resr_name":"Users",
        #     "resr_pulse_module":MODULE,
        #     "resr_type":"firestore_collection",
        #     "resr_classifications":{ "auth_required_confidential"},
        #     "resr_contents":{"user_core_profile"},
        #     "resr_original_or_processed":"original_source",
        #     "resr_origin":"internal",
        #     "resr_origin_organisations_uids":{"20231220futureedgegroup_coreorgn"},
        # }

# Annotated[str, {"resr_classification":"auth_required_restricted",
#                                 "resr_readable_by": ["owner", "selected_by_admin"],
#                                 "resr_updatable_by": ["admin"],
#                                 "resr_original_or_processed" : "original_source",
#                                 "resr_origin":"internal",
#                                 "resr_origin_organisation_uids":["20231220futureedgegroup_coreorgn"], 
#                                 "resr_origin_description":"Original User field",
#                                 "resr_creat_date":datetime(2023, 12, 23),
#                                 "resr_creat_by_user":"Russlan Ramdowar;russlan@ftredge.com",
#                                 "metadata_updt_date":datetime(2023, 12, 23), 
#                                 "metadata_updt_by_user":"Russlan Ramdowar;russlan@ftredge.com"}] 

#  metadata={"resr_classification":"auth_required_restricted",
#                                 "resr_readable_by": ["owner", "selected_by_admin"],
#                                 "resr_updatable_by": [],
#                                 "resr_original_or_processed" : "original_source",
#                                 "resr_origin":"internal",
#                                 "resr_origin_organisation_uids":["20231220futureedgegroup_coreorgn"], 
#                                 "resr_origin_description":"Original User field",
#                                 "resr_creat_date":datetime(2023, 12, 23),
#                                 "resr_creat_by_user":"Russlan Ramdowar;russlan@ftredge.com",
#                                 "metadata_updt_date":datetime(2023, 12, 23), 
#                                 "metadata_updt_by_user":"Russlan Ramdowar;russlan@ftredge.com"}

#   metadata={"resr_classification":"auth_required_restricted",
#                                 "resr_readable_by": ["owner", "selected_by_admin"],
#                                 "resr_updatable_by": ["owner","admin"],
#                                 "resr_original_or_processed" : "original_source",
#                                 "resr_origin":"internal",
#                                 "resr_origin_organisation_uids":["20231220futureedgegroup_coreorgn"], 
#                                 "resr_origin_description":"Original User field",
#                                 "resr_creat_date":datetime(2023, 12, 23),
#                                 "resr_creat_by_user":"Russlan Ramdowar;russlan@ftredge.com",
#                                 "metadata_updt_date":datetime(2023, 12, 23), 
#                                 "metadata_updt_by_user":"Russlan Ramdowar;russlan@ftredge.com"}
  
#     metadata={"resr_classification":"auth_required_confidential",
#                                 "resr_readable_by": ["owner", "selected_by_admin"],
#                                 "resr_updatable_by": ["admin"],
#                                 "resr_original_or_processed" : "original_source",
#                                 "resr_origin":"internal",
#                                 "resr_origin_organisation_uids":["20231220futureedgegroup_coreorgn"], 
#                                 "resr_origin_description":"Original User field",
#                                 "resr_creat_date":datetime(2023, 12, 23),
#                                 "resr_creat_by_user":"Russlan Ramdowar",
#                                 "metadata_updt_date":datetime(2023, 12, 23), 
#                                 "metadata_updt_by_user":"Russlan Ramdowar"}
    
#      metadata={"resr_classification":"auth_required_confidential",
#                                 "resr_readable_by": ["owner", "selected_by_admin"],
#                                 "resr_updatable_by": ["selected_by_admin"],
#                                 "resr_original_or_processed" : "original_source",
#                                 "resr_origin":"internal",
#                                 "resr_origin_organisation_uids":["20231220futureedgegroup_coreorgn"], 
#                                 "resr_origin_description":"Original User field",
#                                 "resr_creat_date":datetime(2023, 12, 23),
#                                 "resr_creat_by_user":"Russlan Ramdowar",
#                                 "metadata_updt_date":datetime(2023, 12, 23), 
#                                 "metadata_updt_by_user":"Russlan Ramdowar"}

class ResourceCatalogItem(BaseModel):

    resr_puid_or_name: str #Ex: username
    resr_path: str #Ex: ipulse-401013/cloud/firesotre/Users/{user_uid}/username
    resr_name: str #Ex: username
    resr_pulse_module: str  #Ex: core 
    resr_type: str
    resr_classifications: Set[str] 
    resr_contents:Set[str]
    resr_original_or_processed: str
    resr_origin: str
    resr_origin_organisations_uids: Set[str]
    resr_origin_description: str
    resr_licences_types: Set[str]
    resr_description_details: str 
    resr_updtbl_by_non_staff: bool
    resr_creat_by_user_uid: str
    resr_creat_date: datetime
    class_version:float = CLASS_VERSION
    resr_columns_count: int
    resr_columns: Optional[Dict[Any, Any]] = None #OPTIONAL
    resr_structure_version: Optional[str]=None # OPTIONAL
    resr_structure_updt_date: Optional[str]=None #OPTIONAL
    resr_structure_updt_by_user_uid: Optional[str]=None # OPTIONAL
    resr_tags: Optional[Dict[Any, Any]] = None #OPTIONAL
    resr_content_updt_date: Optional[str]=None #OPTIONAL
    resr_content_updt_by_user_uid: Optional[str]=None # OPTIONAL
    puid: Optional[str] = None #TO BE SETUP BY Validator
    metadata_version: Optional[float] = None #TO BE SETUP BY  Validator
    metadata_creat_date: Optional[datetime] = None #TO BE SETUP BY Management Service
    metadata_creat_by: Optional[str] = None #TO BE SETUP BY Management Service
    metadata_updt_date: Optional[datetime] = None #TO BE SETUP BY Management Service
    metadata_updt_by: Optional[str] = None #TO BE SETUP BY Management Service
     
    @validator('puid', pre=True, always=True)
    def set_puid(cls, puid, values):
        if puid is None:
            return f"{datetime.utcnow().strftime('%Y%m%d%H%M')}{uuid.uuid4().hex[:8]}_{MODULE}{CLASS_REF}".lower()
        return puid
    
    @validator('metadata_version', pre=True, always=True)
    def set_metadata_version(cls, metadata_version, values):
        if metadata_version is None:
            return 1.0
        else: 
            return metadata_version + 0.1


    @validator('resr_pulse_module', pre=True, always=True)
    def validate_resr_pulse_module(cls, resr_pulse_modules):
        if resr_pulse_modules not in enums.pulse_modules:
            raise ValueError("Invalid pulse_modules values provided.")
        return resr_pulse_modules
    
    @validator('resr_type', pre=True, always=True)
    def validate_resr_type(cls, resr_type):
        if  resr_type not in enums.resource_types:
            raise ValueError("Invalid resource_types value provided.")
        return resr_type
    
    @validator('resr_classifications', pre=True, always=True)
    def validate_resr_classifications(cls, resr_classifications):
        if not resr_classifications.issubset(enums.resource_classifications):
            raise ValueError("Invalid resr_classifications values provided.")
        return resr_classifications

    @validator('resr_contents', pre=True, always=True)
    def validate_resr_contents(cls, resr_contents):
        if not resr_contents.issubset(enums.resource_contents):
            raise ValueError("Invalid resr_contents values provided.")
        return resr_contents

    @validator('resr_original_or_processed', pre=True, always=True)
    def validate_resr_original_or_processed(cls, resr_original_or_processed):
        if  resr_original_or_processed not in enums.resource_original_or_processed:
            raise ValueError("Invalid resr_original_or_processed value provided.")
        return resr_original_or_processed
    
    @validator('resr_origin', pre=True, always=True)
    def validate_resr_origin(cls, resr_origin):
        if  resr_origin not in enums.resource_origins:
            raise ValueError("Invalid resource_origins value provided.")
        return resr_origin
       

    @validator('metadata_creat_date', 'metadata_updt_date', pre=True)
    def parse_date(cls, value):
        if value is None:
            return value
        if isinstance(value, datetime):
            return value
        try:
            # Assuming Firestore returns an ISO 8601 string, adjust if necessary
            return dateutil.parser.isoparse(value)
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid datetime format inside Resource Description: {value}")


    
    @validator('metadata_updt_date', 'metadata_updt_date', pre=True, always=True)
    def set_default_updt_date(cls, date, values):
        if date is None:
            return datetime.utcnow().isoformat()
        return date