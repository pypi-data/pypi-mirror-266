import json
from datetime import datetime, timedelta, timezone
from typing import Any, List

from dpd_lib.client.exceptions import (
    BadQueryException,
    BucketNotFoundException,
    InfluxNotAvailableException,
)
from dpd_lib.models import InfluxInfrasoundRecord
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.rest import ApiException
from loguru import logger
from pydantic import SecretStr
from urllib3.exceptions import NewConnectionError


class InfluxClient:
    """
    A restricted client wihcih implements an intervface
    to query data from the influx database.
    """

    MEASUREMENT_NAME: str = "infrasound"

    def __init__(
        self, bucket: str, token: SecretStr, org: str, url: str
    ) -> None:
        self.bucket = bucket
        self._client = InfluxDBClient(
            url=url, token=token.get_secret_value(), org=org
        )

    async def record_infrasound(
        self, type: str, value: float, station: str, timestamp: datetime
    ) -> None:
        """
        Records new infrasound record for a given timestamp

        Arguments:
            type (str): The type of infrasound record
            value (float): The value of the record
            station (str): The associated station
            timestamp (datetime): The timestamp

        Returns:
            None
        """

        p = (
            Point(type)
            .tag("station", station)
            .field(type, value)
            .time(timestamp)
        )
        await self._insert(p)

    async def read_infrasound(
        self,
        type: str = "",
        stations: List[str] = [],
        t0: datetime = datetime.now(timezone.utc) - timedelta(seconds=15),
        t1: datetime = datetime.now(timezone.utc),
    ) -> List[InfluxInfrasoundRecord]:
        """
        Reads infrasound records for a given type, station list, and timestamp

        Arguments:
            type (str): The type of infrasound record
            station (List(str)): The station of infrasound record
            t0 (datetime): the beginning of the timerange
            t1 (datetime): The end of the timerange

        Returns:
            res(List[InfluxInfrasoundRecord]): All records of a
            certain type for a given range.
        """
        query = """from(bucket:"{0}")
        |> range(start: {1}, stop: {2})""".format(
            self.bucket,
            t0.strftime("%Y-%m-%dT%H:%M:%SZ"),
            t1.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        if type != "":
            query += '|> filter(fn:(r) => r._measurement == "{0}")'.format(
                type
            )
        if len(stations) != 0:
            query += """
            |> filter(fn:(r) => contains(value: r.station, set: {0}))
            """.format(
                json.dumps(stations)
            )
        return await self._query(query)

    async def list_infrasound(
        self,
        t0: datetime = datetime.now(timezone.utc) - timedelta(seconds=15),
        t1: datetime = datetime.now(timezone.utc),
    ) -> List[InfluxInfrasoundRecord]:
        """
        Lists all records for given time range.

        Arguments:
            t0 (datetime): the beginning of the timerange
            t1 (datetime): The end of the timerange

        Returns:
            res (List[InfluxInfrasoundRecord]):
                All records for given time range.
        """

        return await self.read_infrasound(type="", stations=[], t0=t0, t1=t1)

    async def _insert(self, p: Point) -> Any:
        """
        Inserts a point into the database via InfluxDB write_api

        Arguments:
            p (Point): The data point to insert into the database

        Returns:
            res (Any): Results from the write_api
        """
        write_api = self._client.write_api(write_options=SYNCHRONOUS)
        try:
            res = write_api.write(bucket=self.bucket, record=p)
        except NewConnectionError:
            raise InfluxNotAvailableException()
        except ApiException as e:
            if e.status and e.status == 400:
                raise BadQueryException()
            if e.status and e.status == 404:
                raise BucketNotFoundException()
            raise InfluxNotAvailableException()
        logger.info(f"{res=}")
        return res

    async def _query(self, query: str = "") -> List[InfluxInfrasoundRecord]:
        """
        Queries the InfluxDB with the proivded query string

        Arguments:
            query (str): The raw query string to pass to InfluxDB

        Returns:
            res (List[InfluxInfrasoundRecord]):
                A list of records that match the query
        """
        logger.debug(f"Running {query=}")
        query_api = self._client.query_api()
        try:
            result = query_api.query(query=query)
        except NewConnectionError:
            raise InfluxNotAvailableException()
        except ApiException as e:
            if e.status and e.status == 400:
                raise BadQueryException()
            if e.status and e.status == 404:
                raise BucketNotFoundException()
            raise InfluxNotAvailableException()
        res = []
        for table in result:
            for record in table.records:
                logger.debug(record)
                logger.debug(record.get_measurement())
                logger.debug(record.values.get("station"))
                logger.debug(record.get_time())
                r = InfluxInfrasoundRecord(
                    type=record.get_measurement(),
                    station=record.values.get("station"),
                    timestamp=record.get_time(),
                    value=record.get_value(),
                )
                res.append(r)
        logger.debug(f"Query retgurned {len(res)} records.")
        return res
