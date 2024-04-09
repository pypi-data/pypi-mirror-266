from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from dpd_lib.models import InfluxInfrasoundRecord


class InsertInfrasoundRequest(BaseModel):
    type: str = Field(description="Type of infrasound record")
    value: float = Field(description="Value of infrasound record")
    station: str = Field(description="Station associated with record")
    timestamp: datetime = Field(description="record timestamp")


class InsertInfrasoundResponse(BaseModel):
    bucket: str = Field(description="Name of the requested bucket")
    type: str = Field(description="Type of infrasound record")
    value: float = Field(description="Value of infrasound record")
    station: str = Field(description="Station associated with record")
    timestamp: datetime = Field(description="record timestamp")


class ListInfrasoundResponse(BaseModel):
    bucket: str = Field(description="Name of the requested bucket")
    records: List[InfluxInfrasoundRecord] = Field(
        description="Contents of requested bucket"
    )
