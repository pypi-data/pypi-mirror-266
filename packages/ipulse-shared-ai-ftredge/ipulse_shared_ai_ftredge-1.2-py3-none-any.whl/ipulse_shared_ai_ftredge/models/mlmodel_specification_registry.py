from pydantic import BaseModel, Field,validator, ValidationError
from typing import List, Optional, Dict, Union
from datetime import datetime
from enum import Enum
from app.models.po_abstract import POAbstract
from enum import Enum


CLASS_ORIGIN_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_ORGIN_DATE=datetime(2024, 3, 26, 18, 00)

CLASS_VERSION = 2.01
CLASS_REVISION_AUTHOR="Russlan Ramdowar;russlan@ftredge.com"
CLASS_ORGIN_DATE=datetime(2024, 3, 26, 18, 00)

class MLModelSpecificationRegistry(BaseModel):
    
    # ml_models_specifications_registry: Optional[Dict[str, Dict[str,Dict[str, Union[str, List[str]]]]]]
    ## {1Y:{"total":5, "model_uid1":{"architecture": , "accuracy": , "last_output_datetime": , "description":"5 minutes interval data from EoD API and Twelve API","sources":["EoD","Twelve"]
   
   po_funancial_series_uid: str
   prediction_range: str #1Y, 5Y, 10Y
   total_nb_model_specifications: int = 0
   models_specifications: Optional[Dict[str, Dict[str,Union[str, List[str]]]]] ## THIS SHOULD BE CREATE BY A FUNCTION IN THE MLModelSpecification
   ## {"model_uid1":{"architecture":"arc", "metric1":0.55, "metric2":0.99 , "last_output_datetime": , "latest_predictions_series_uid":"predictions54545dfvdf", "description":"5 minutes interval data from EoD API and Twelve API","author":["Russlan"]}