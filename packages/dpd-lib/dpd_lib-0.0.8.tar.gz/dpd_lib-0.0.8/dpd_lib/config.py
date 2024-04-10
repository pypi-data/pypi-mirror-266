import os
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    influx_bucket: Optional[str] = os.environ.get("INFLUX_BUCKET")
    influx_url: Optional[str] = os.environ.get("INFLUX_URL")
    influx_token: SecretStr = os.environ.get("INFLUX_TOKEN")
    influx_org: Optional[str] = os.environ.get("INFLUX_ORG")


settings = Settings()
