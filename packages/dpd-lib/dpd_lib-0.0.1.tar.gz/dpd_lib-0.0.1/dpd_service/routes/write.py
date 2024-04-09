from fastapi import APIRouter, HTTPException
from loguru import logger

from client.influx import (
    BadQueryException,
    BucketNotFoundException,
    InfluxClient,
    InfluxNotAvailableException,
)
from dpd_lib.config import settings
from schemas import (
    InsertInfrasoundRequest,
    InsertInfrasoundResponse,
)

write_router = APIRouter(prefix="/write")


@write_router.post(
    "/{bucket}/insert",
    summary="Insert data intgo a bucket.",
    responses={
        201: {"description": "Successfully Inserted Into Bucket."},
        400: {"description": "Bad data requested."},
        404: {"description": "Bucket not found."},
        503: {"description": "InfluxDB Not Available."},
    },
)
async def insert_bucket(
    r: InsertInfrasoundRequest, bucket: str
) -> InsertInfrasoundResponse:
    logger.debug(f"Insert data into {bucket=}")
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
        await ic.record_infrasound(r.type, r.value, r.station, r.timestamp)
    except (
        InfluxNotAvailableException,
        BucketNotFoundException,
        BadQueryException,
    ) as e:
        raise HTTPException(
            status_code=e.STATUS_CODE,
            detail=e.DESCRIPTION,
        )
    logger.debug(
        f"Inserted data into {bucket=} with {r.location=} and {r.height}"
    )
    return InsertInfrasoundResponse(
        bucket,
        type=r.type,
        value=r.value,
        station=r.station,
        timestamp=r.timestamp,
    )
