from pydantic import BaseModel, Field,validator, ValidationError
from typing import List, Optional, Dict
from datetime import datetime


CLASS_ORIGIN_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_ORGIN_DATE=datetime(2024, 3, 26, 18, 00)

CLASS_VERSION = 2.01
CLASS_REVISION_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_ORGIN_DATE=datetime(2024, 3, 26, 18, 00)


####PredictableObject
class POAbstract(BaseModel):
    schema_version: float = Field(default=CLASS_VERSION, description="Version of this Class == version of DB Schema") #User can Read only
    short_name: str
    target_var_column_name: str
    
    data_domain: str #oracle/historical/ or oracle/predictions/ or gym/historical
    category: str  # indices,  crypto, stocks , commodities, real_estate, forex, options, bonds, funds, watches, cars, art, wine, collectibles, weather, other
    
    tags: Dict[str, str]
    description: str
       
    creat_datetime: datetime
    creat_by_userauthuid: str
    updt_datetime: datetime
    updt_by_userauthuid: str 
   
    @property
    def full_name(self) -> str:
        return f"{self.short_name}_{self.data_domain}_{self.asset_category}_{self.target_var_column_name}"


 
#POAbstract: BTC -> financial,crypto, ["BTC","Bitcoin","cryptocurrency"], {"source":"Binance","data_origin":"API","data_origin_description":"Binance API","frequency":"1m","fill":"ffill"}, ["BTC_1m_2024-03-26_18:00","BTC_5m_2024-03-26_18:00"], ["model1","model2"], datetime(2024, 3, 26, 18, 00), "userauthuid", datetime(2024, 3, 26, 18, 00), "userauthuid"
#can have several POSeriesAbstract
#POSeriesAbstract : btc_eod -> [ 5m , 6M, 1Y, 5Y, 10Y ]
# has sequence of POSeries depending on historical size ; is inside a MLModelSpecificationRegistry
#POSeries: ["2024-03-26_18:00",35006.58], ["2024-03-26_18:05",35050.64].....

# each MLModelSpecification has many MLModelInstances, which are the trained models. Training happens according to the training/state_update strategy described the MLModelSpecification
# MLModelSpecification describes architecture,  hyperparameters,  features (inputs) of the model and update_strategy. It is belonging to a specific interval series (like BTC 5m)
# MLModelInstancePredictionsRegistry is a registry of predictions for a given MLModelInstance
# It can be that several MLModelInstances with exact same specifications except for update_strategy are used to give predictions for a single POSeries 
# ##  on overlapping intervals which doesn't make practical sense from user's perspective but does for metrics and understanding how much tightly fit models are to the data
# ##  we assume that the simpler the model the more dependant it is on retraining/state_update. User will ofcourse prefer the most frequently retrained model,
# ##  however that comes with a $$. We want to find a good balance.

# MLModelInstanceMetricsRegistry is a registry of metrics for a given MLModelInstance
# MLModelSpecificationMetricsRegistry is a registry of metrics for a given MLModelSpecification (whcih will be used to average out the metrics of all models with same specs and training strategy)



# As a customer I want to 
# See a List of Asset Categories
# Inside each List of Asset Categories, see a list of Assets (Bitcoin, Apple, Gold...) 
# Choose an Asset and have default view displayed ( default POSeries i.e. BTC 5m)
# Select a horizon for Oracle Prediction (1D, 5D, 1M, 6M, 1Y, 3Y, 10Y, 25Y) and see availble ML Models with their InsisgtCredits cost
# Those available Models should be sorted by their performance metrics (choose one, but various sorting should be possible)
# Select a ML Model and see the performance metrics in details
# When a user views specific MlModelInstancePredictions , this should be recorded in his "views" history
# User shall be able to select multiple predictions and see all of them displayed on the chart. (Optional, he should be able to take a screenshot and save it)


