from typing import Dict, Optional, Any
import pandas as pd
from ipulse_shared_ai_ftredge.models.po_series import POSeries

def split_large_pandaseries_to_chunked_poseries(
    simulated_series: pd.Series,
    name: str,
    data_domain: str,
    asset_category: str,
    frequency: str,
    OHLCV: str,
    creat_by_userauthuid: str,
    updt_by_userauthuid: str,
    chunk_size: int = 2000,
    tags: Optional[Dict[Any, Any]] = None,
    description: Optional[str] = None,
    series_main_origin_short: Optional[str] = None,
    series_main_origin_source: Optional[Dict[Any, Any]] = None,
    
    
) -> Dict[str, POSeries]:
    """
    Splits a large series into chunks, creates associated POSeries objects with 
    provided attributes, and returns them as a dictionary.

    Returns:
        Dict[str, POSeries]: A dictionary mapping unique IDs (UIDs) to POSeries objects.
    """

    if simulated_series.empty:
        raise ValueError("Input series cannot be empty")

    if chunk_size <= 0 or not isinstance(chunk_size, int) or chunk_size > 5000:
        raise ValueError("Chunk size must be a positive integer less than or equal to 5000")

    # Check for missing required attributes
    required_attributes = [
        "name",
        "data_domain",
        "asset_category",
        "frequency",
        "OHLCV",
        "creat_by_userauthuid",
        "updt_by_userauthuid",
    ]
    missing_attributes = [attr for attr in required_attributes if locals()[attr] is None]
    if missing_attributes:
        raise ValueError(f"Missing required attributes: {', '.join(missing_attributes)}")

    series_registry = {}  # Dictionary to store POSeries objects

    # Split data into chunks
    for start_idx in range(0, len(simulated_series), chunk_size):
        end_idx = min(start_idx + chunk_size, len(simulated_series))
        chunk_series = simulated_series.iloc[start_idx:end_idx]

        # Create POSeries object
        po_series_object = POSeries(
            name=name,
            data_domain=data_domain,
            asset_category=asset_category,
            frequency=frequency,
            OHLCV=OHLCV,
            tags=tags,
            description=description,
            series_main_origin_short=series_main_origin_short,
            series_main_origin_source=series_main_origin_source,
            creat_by_userauthuid=creat_by_userauthuid,
            updt_by_userauthuid=updt_by_userauthuid,
            last_updt_action="create",
            series=chunk_series,
        )

        series_registry[po_series_object.uid] = po_series_object
        
    return series_registry