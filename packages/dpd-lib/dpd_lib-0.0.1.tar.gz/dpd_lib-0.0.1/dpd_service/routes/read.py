from datetime import datetime, timedelta, timezone
from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Query, Request
from loguru import logger

from dpd_lib.client.influx import (
    BadQueryException,
    BucketNotFoundException,
    InfluxClient,
    InfluxNotAvailableException,
)
from dpd_lib.config import settings
from schemas import ListInfrasoundResponse

read_router = APIRouter(prefix="/read")


@read_router.get(
    "/{bucket}/query",
    summary="Queries a bucket's contents.",
    responses={
        201: {"description": "Successfully Inserted Into Bucket."},
        400: {"description": "Bad data requested."},
        404: {"description": "Bucket not found."},
        503: {"description": "InfluxDB Not Available."},
    },
)
async def query_bucket(
    r: Request,
    bucket: str,
    type: str = "",
    stations: List[str] = Query(
        None
    ),  # stations: Annotated[List[str] | None, Query()] = None,
    t0: datetime = datetime.now(timezone.utc) - timedelta(seconds=15),
    t1: datetime = datetime.now(timezone.utc),
) -> ListInfrasoundResponse:
    logger.debug(
        f"Querying {bucket=} with {type=} and {t0} starttime and {t1} endtime at {stations=}"
    )
    if settings.influx_token and settings.influx_org and settings.influx_url:
        ic = InfluxClient(
            bucket,
            settings.influx_token,
            settings.influx_org,
            settings.influx_url,
        )
    else:
        logger.error("Please set the influx environment variables.")

    try:
        records = await ic.read_infrasound(
            type=type, stations=stations, t0=t0, t1=t1
        )
    except (
        InfluxNotAvailableException,
        BucketNotFoundException,
        BadQueryException,
    ) as e:
        raise HTTPException(
            status_code=e.STATUS_CODE,
            detail=e.DESCRIPTION,
        )
    logger.debug(f"Records fetched {records=}")
    return ListInfrasoundResponse(bucket=bucket, records=records)


@read_router.get(
    "/{bucket}/list",
    summary="Lists a bucket's contents",
    responses={
        201: {"description": "Successfully Inserted Into Bucket."},
        404: {"description": "Bucket not found."},
        503: {"description": "InfluxDB Not Available."},
    },
)
async def list_bucket(
    r: Request,
    bucket: str,
    t0: datetime = datetime.now(timezone.utc) - timedelta(seconds=15),
    t1: datetime = datetime.now(timezone.utc),
) -> ListInfrasoundResponse:
    logger.debug(f"Listing {bucket=} between {t0} starttime and {t1} endtime")
    if settings.influx_token and settings.influx_org and settings.influx_url:
        ic = InfluxClient(
            bucket,
            settings.influx_token,
            settings.influx_org,
            settings.influx_url,
        )
    else:
        logger.error("Please set the influx environment variables.")

    try:
        records = await ic.list_infrasound(t0=t0, t1=t1)
    except (
        InfluxNotAvailableException,
        BucketNotFoundException,
        BadQueryException,
    ) as e:
        raise HTTPException(
            status_code=e.STATUS_CODE,
            detail=e.DESCRIPTION,
        )
    logger.debug(f"Records fetched {records=}")
    return ListInfrasoundResponse(bucket=bucket, records=records)
