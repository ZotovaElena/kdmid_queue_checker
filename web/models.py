from pathlib import Path
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, validator, Field


class CheckingExpectModel(BaseModel):

    kdmid_subdomain : str = Field(..., example='madrid')
    order_id : str = Field(..., example='130238')
    code : str = Field(..., example='CD9E05C1')
    every_hours : int = Field(..., example=2)

    __annotations__ = {
        "kdmid_subdomain": str,
        "order_id": str,
        "code": str,
        "every_hours": int
    }
    class Config: 
        schema_extra = {
            "example": {
                "kdmid_subdomain": "madrid",
                "order_id": "130238",
                "code": "CD9E05C1",
                "every_hours": 2
            }
        }

class CheckingResponseModel(BaseModel):
    status: str = Field(..., example='success')
    message: str = Field(..., example='The queue is over')
    __annotations__ = {
        "status": str,
        "message": str
    }
    class Config: 
        schema_extra = {
            "example": {
                "status": "success",
                "message": "The queue is over"
            }
        }