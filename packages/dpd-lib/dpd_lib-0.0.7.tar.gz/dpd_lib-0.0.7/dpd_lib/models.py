from datetime import datetime

from pydantic import BaseModel, Field


class InfluxInfrasoundRecord(BaseModel):
    type: str = Field(description="Type of infrasound record")
    value: float = Field(description="Value of infrasound record")
    station: str = Field(description="Station associated with record")
    timestamp: datetime = Field(description="record timestamp")
