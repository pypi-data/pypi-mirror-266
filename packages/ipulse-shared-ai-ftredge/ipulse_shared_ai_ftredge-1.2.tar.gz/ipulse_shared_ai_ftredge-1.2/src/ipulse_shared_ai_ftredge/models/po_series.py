from pydantic import BaseModel,validator, model_validator, Field   #, field_serializer, AwareDatetime
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone
import pandas as pd
import uuid
import re
import pytz
#  I want you to add methods which will allow for adding, updating or deleting  series to series_registry, with keys being interval to which series relates to such as "5m" , "10m" etc. . When adding a series an origin must be added to series_origin_sources , 

CLASS_ORIGIN_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_ORGIN_DATE=datetime(2024, 3, 26, 18, 00)

CLASS_VERSION = 2.01
CLASS_REVISION_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
LAST_MODIFICATIONS=["Fixed creat and udpate datestimes ","Modified fields in a way to not require POSeriesAbstract"]

MAXIMUM_SERIES_CHUNK_SIZE=2000
class POSeries(BaseModel):
   
    name: str #apple
    @validator('name')
    def validate_name(cls, value):
        if len(value) >= 15:
            raise ValueError("name must be less or equal to 10 characters")
        if not re.match(r"^[a-zA-Z0-9 ]+$", value):
            raise ValueError("name must not contain special characters")
        value = value.lower()
        return value
    tags: Optional[Dict[Any, Any]]=None
    symbol: Optional[str] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None
    frequency: str # 30S, 1min, 5min, 15min, 30min, H, 4H, D (or B which is Business Day), 3D, W, 3W,  M, (or BM as last business day of the month), Y (or BY)
    description: str
    fill: Optional[str]=None #ffill, bfill, linear, spline, mean, median, mode, zero, constant
    OHLCV: str #Open, High, Low, Close, Volume
    @validator("OHLCV")
    def validate_OHLCV(cls, value):
        valid_values = ["o", "h", "l", "c", "v", "adjc"]
        if value not in valid_values:
            raise ValueError(f"{value} is not a valid OHLCV. Valid values are: {', '.join(valid_values)}")
        return value
 
    data_domain: str #oracle/historical/ or oracle/predictions/ or gym/historical
    asset_category: str  # indices,  crypto, stocks , commodities, real_estate, forex, options, bonds, funds, watches, cars, art, wine, collectibles, weather, other
 
    @validator('asset_category')
    def validate_asset_category(cls, value):
        valid_categories = ["indcs", "crypto", "stocks", "commdts", "rel_est", "forex", 
                            "options", "bonds", "funds", "corpfundam", "economcs","energy", "luxury", "art", "wine", 
                            "clctbls", "weather", "climate", "sports", "health", "transprt", "astronmcl", "simultn", "other" ]
        if value not in valid_categories:
            raise ValueError(f"asset_category '{value}' is not valid. Must be one of: {', '.join(valid_categories)}")
        return value
    
    series_main_origin_short: Optional[str]= None #brief description of the source
    @validator('series_main_origin_short')
    def validate_series_main_origin_short(cls, value):
        if len(value) >= 6:
            raise ValueError("series_main_origin_short must be less or equal to 6 characters")
        return value
    series_main_origin_source:Dict[Any, Any] #immediate origin per series -> doc paths until uids or bigquery table path if within PULSE, full api path if external
    series_main_origin_description: Optional[str]=None #description of the source
    
    series_timezone: str
    @validator("series_timezone")
    def validate_series_timezone(cls, value):
        valid_values = [
                        'UTC',  # Coordinated Universal Time
                        'America/New_York',  # Eastern Standard Time / Eastern Daylight Time (New York)
                        'America/Los_Angeles',  # Pacific Standard Time / Pacific Daylight Time (Los Angeles)
                        'Europe/London',  # Greenwich Mean Time / British Summer Time (London)
                        'Asia/Shanghai',  # China Standard Time (Shanghai)
                        'Asia/Tokyo',  # Japan Standard Time (Tokyo)
                        'Asia/Kolkata',  # Indian Standard Time (Mumbai)
                        'Asia/Hong_Kong',  # Hong Kong Time
                        'Australia/Sydney',  # Australian Eastern Daylight Time / Australian Eastern Standard Time (Sydney)
                        'Europe/Moscow'  # Moscow Standard Time (Moscow)
                    ]
        if value not in valid_values:
            raise ValueError(f"{value} is not a valid OHLCV. Valid values are: {', '.join(valid_values)}")
        return value
    
    series: Union[Dict[str, float], pd.Series] # series: pd.Series = pd.Series(dtype='float64') # series_frame:pd.DataFrame = pd.DataFrame(dtype='float64') # "Open", "High", "Low", "Close", "Volume"
    
    @validator('series', pre=True)  # Use `pre=True` to convert before other validations
    def convert_series_if_needed(cls, value):
        if isinstance(value, pd.Series):
            # Convert pd.Series to dictionary with datetime keys
            value = convert_pandasseries_to_dictseries(value)
        return value

    @validator('series')
    def validate_series_length(cls, value: Dict[str, float]):
        if len(value) > MAXIMUM_SERIES_CHUNK_SIZE:
            raise ValueError(f"The length of the series must not exceed {MAXIMUM_SERIES_CHUNK_SIZE} elements")
        return value
    
    # @field_serializer('series')
    # def serialize_series(self, series: pd.Series) -> List[Dict[str, Any]]:
    #     records = [{"date": index.isoformat(), self.OHLCV: value} for index, value in series.items()]
    #     return records
    
    # Calculated attributes based on series_frame
    start_datetime: Optional[datetime] = None 
    end_datetime: Optional[datetime] = None
    total_intervals_count: Optional[int] = None
    
    series_data_version: int = 1
    creat_datetime: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    creat_by_userauthuid: str
    updt_datetime: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updt_by_userauthuid: str
    last_updt_action: str
    @validator("last_updt_action")
    def validate_update_action(cls, value):
        valid_actions = ["create", "prepend", "append", "amend", "insert_single", "merge", "delete"]
        if value not in valid_actions:
            raise ValueError(f"{value} is not a valid update action. Valid actions are: {', '.join(valid_actions)}")
        return value
 
    uid:Optional[str] = None #stocks_apple_5min_c_202403310905_202403311705_yahoo"
    
    @model_validator(mode='after') # This validator now has priority 1 and will run before add_uid
    def calculate_derived_attributes(self):
        if self.series:  # Checks if the series dictionary is not empty
            
            datetime_keys = [datetime.fromisoformat(k) for k in self.series.keys()]
            self.start_datetime = min(datetime_keys)
            self.end_datetime = max(datetime_keys)
            self.total_intervals_count = len(self.series)
        else:
            # Handle case where series is empty
            self.start_datetime = None
            self.end_datetime = None
            self.total_intervals_count = 0
        return self
    
    @model_validator(mode='after')  # This validator now has priority 2 and will run after calculate_derived_attributes
    def add_uid(self):
        if not self.uid:
            uid = f"{self.asset_category}_{self.name}_{self.frequency}_{self.OHLCV}_{self.start_datetime.strftime('%Y%m%d%H%M')}_{self.total_intervals_count}_{self.series_main_origin_short}"
            if len(uid) > 80:
                raise ValueError("The length of uid must not exceed 80 characters")
            self.uid = uid
        return self
    
    @staticmethod
    def from_pandasseries_chunk(chunk_series: pd.Series, **kwargs) -> "POSeries":
        # series_dict = {index.isoformat(): value for index, value in chunk_series.items()}
        series_dict=convert_pandasseries_to_dictseries(chunk_series)
        kwargs['series'] = series_dict
        return POSeries(**kwargs)
    
    @staticmethod
    def from_dict_series_chunk(series_dict: Dict[str, float], **kwargs) -> "POSeries":
        kwargs['series'] = series_dict
        return POSeries(**kwargs)

    class Config:
        arbitrary_types_allowed = True
        # json_encoders = {
        #     datetime: lambda v: v.isoformat(),
        # }

def convert_pandasseries_to_dictseries(series: pd.Series) -> Dict[str, float]:
    return {index.isoformat(): value for index, value in series.items()}

def convert_dictseries_to_pandasseries(dict_series: Dict[str, float]) -> pd.Series:
    series = pd.Series({pd.to_datetime(iso_date): value for iso_date, value in dict_series.items()})
    
    # Optionally, sort the series by its index (datetime) if needed
    series = series.sort_index()
    
    return series

def split_large_pandasseries_to_chunked_poseries(
    large_series: pd.Series,
    chunk_size: int = MAXIMUM_SERIES_CHUNK_SIZE,
    **kwargs,
) -> Dict[str, POSeries]:
    if large_series.empty:
        raise ValueError("Input series cannot be empty")
    if chunk_size <= 0 or chunk_size > MAXIMUM_SERIES_CHUNK_SIZE:
        raise ValueError(f"Chunk size must be a positive integer less than or equal to {MAXIMUM_SERIES_CHUNK_SIZE}")

    series_registry = {}

    for start_idx in range(0, len(large_series), chunk_size):
        end_idx = min(start_idx + chunk_size, len(large_series))
        chunk_series = large_series.iloc[start_idx:end_idx]

        po_series_object = POSeries.from_pandasseries_chunk(chunk_series, **kwargs)
        series_registry[po_series_object.uid] = po_series_object

    return series_registry

def split_large_dictseries_to_chunked_poseries(
    series_dict: Dict[str, float],
    chunk_size: int = MAXIMUM_SERIES_CHUNK_SIZE,
    **kwargs,
) -> Dict[str, POSeries]:
    if not series_dict:
        raise ValueError("Input series cannot be empty")
    if chunk_size <= 0 or chunk_size > MAXIMUM_SERIES_CHUNK_SIZE:
        raise ValueError(f"Chunk size must be a positive integer less than or equal to {MAXIMUM_SERIES_CHUNK_SIZE}")

    series_registry = {}

    # Split the series dictionary into chunks and create POSeries objects
    items = list(series_dict.items())
    for start_idx in range(0, len(items), chunk_size):
        chunk_items = items[start_idx:start_idx + chunk_size]
        chunk_dict = {item[0]: item[1] for item in chunk_items}

        # Create a POSeries object for each chunk
        # Ensure POSeries.from_dict_series or a similar method exists and is capable of handling this data structure
        po_series_object = POSeries.from_dict_series(chunk_dict, **kwargs)
        series_registry[po_series_object.uid] = po_series_object

    return series_registry







# def get_series_slice(self, dataset=None, split_ratio=None, indx_end=None, indx_start=None):
#     """
#     Returns extract of the dataset from start till split_ratio, or depending on indx_end and indx_start
#     """
#     if dataset is None:
#         dataset = self.series.copy()

#     if indx_end is not None and indx_start is not None:
#         return dataset.loc[indx_start:indx_end]
#     elif indx_end is not None:
#         return dataset.loc[:indx_end]
#     elif indx_start is not None:
#         return dataset.loc[indx_start:]
#     else:
#         total_len = len(dataset)
#         set_end = int(total_len * split_ratio)
#         return dataset.iloc[:set_end]

# def get_train_valid_test_sets(self, train_split_ratio, valid_split_ratio, frequency=None, fill=None):
#     """
#     Split the entire dataset into training, validation, and test sets.
#     """
#     dataset = self.series.copy()

#     if frequency is not None:
#         dataset = dataset.asfreq(frequency)
#         if fill is not None:
#             dataset = dataset.fillna(method=fill)

#     total_len = len(dataset)

#     train_end = int(total_len * train_split_ratio)
#     valid_end = train_end + int(total_len * valid_split_ratio)

#     train_data = self.get_series_slice(dataset=dataset, split_ratio=train_split_ratio)
#     valid_data = dataset.iloc[train_end:valid_end]
#     test_data = dataset.iloc[valid_end:]

#     return train_data, valid_data, test_data