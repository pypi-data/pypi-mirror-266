from pydantic import BaseModel, Field,validator, ValidationError, model_validator
from typing import List, Optional, Dict, Union, Any
from datetime import datetime, timezone
import uuid
import re

CLASS_ORIGIN_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_ORGIN_DATE=datetime(2024, 3, 26, 18, 00)

CLASS_VERSION = 2.01
CLASS_REVISION_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_REVISION_DATE=datetime(2024, 3, 26, 18, 00)

    
class POSeriesAbstract(BaseModel):
    schema_version: float = Field(default=CLASS_VERSION, description="Version of this Class == version of DB Schema") #User can Read only
    short_name: str
    @validator('short_name')
    def validate_short_name(cls, value):
        if len(value) >= 10:
            raise ValueError("short_name must be less ro equal to 10 characters")
        # Regex explanation:
        # ^ asserts position at start of a string
        # [a-zA-Z0-9 ]+ matches 1 or more of any character in the set (letters, digits, space)
        # $ asserts position at the end of a string
        if not re.match(r"^[a-zA-Z0-9 ]+$", value):
            raise ValueError("short_name must not contain special characters")
        value = value.lower()
        return value
    uid:Optional[str] = None
    target_var_column_name: str
    symbol: Optional[str] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None
 
    data_domain: str #oracle/historical/ or oracle/predictions/ or gym/historical
    asset_category: str  # indices,  crypto, stocks , commodities, real_estate, forex, options, bonds, funds, watches, cars, art, wine, collectibles, weather, other
    
    tags: Dict[str, Any]
    description: str

    series_registry: Optional[Dict[str, Dict[str, Any]]]= None # mapping of Interval to PoFinancialSeries.uids
    # series_registry: Optional[Dict[str, Dict[str,Union[str, List[str]]]]] # mapping of Interval to PoFinancialSeries.uids 
    ## {5m:{"uid":"fdfdf","description":"5m interval data from EoD API and Twelve API","sources":["EoD","Twelve"]
    # ml_models_specifications_registry: Optional[Dict[str, Dict[str,Dict[str, Union[str, List[str]]]]]]
    ## {1Y:{"total":5, "model_uid1":{"architecture": , "accuracy": , "last_output_datetime": , "description":"5 minutes interval data from EoD API and Twelve API","sources":["EoD","Twelve"]
   
    series_origin_brief: Optional[str]= None #brief description of the source
    series_origin_sources:Optional[Dict[str, Any]]= None #immediate origin per series -> doc paths until uids or bigquery table path if within PULSE, full api path if external
    series_origin_description: Optional[Dict[str, Any]]= None #description of the source
    series_earliest_record_datetime: Optional[datetime] = None
    series_latest_record_datetime: Optional[datetime] = None
    series_total_records_count: Optional[int] = None
    
    creat_datetime: datetime =Field(default_factory=lambda: datetime.now(timezone.utc))
    creat_by_userauthuid: str
    updt_datetime: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updt_by_userauthuid: str
    
    @model_validator(mode='after')
    def add_uid(self):
        if not self.uid:
            self.uid = f"{self.short_name}_abs_{datetime.now(timezone.utc).strftime('%Y%m%d')}{uuid.uuid4().hex[:5]}".lower()
        return self

    @property
    def full_name(self) -> str:
        return f"{self.symbol}_{self.currency}_{self.short_name}_{self.series_origin_brief}"