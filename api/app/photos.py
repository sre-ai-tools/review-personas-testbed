"""Item photos in S3. Browsers upload and download directly using short-lived presigned URLs."""

import os
from functools import lru_cache

import boto3

URL_TTL_SECONDS = 300
MAX_PHOTO_BYTES = 5 * 1024 * 1024
EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


@lru_cache(maxsize=1)
def _s3():
    return boto3.client("s3")


def photo_key(item_id: int, content_type: str) -> str:
    return f"items/{item_id}/photo.{EXTENSIONS[content_type]}"


def upload(key: str, content_type: str) -> dict:
    # A presigned POST (unlike PUT) lets S3 enforce the size and type limits.
    return _s3().generate_presigned_post(
        Bucket=os.environ["PHOTOS_BUCKET"],
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[
            {"Content-Type": content_type},
            ["content-length-range", 1, MAX_PHOTO_BYTES],
        ],
        ExpiresIn=URL_TTL_SECONDS,
    )


def download_url(key: str) -> str:
    return _s3().generate_presigned_url(
        "get_object",
        Params={"Bucket": os.environ["PHOTOS_BUCKET"], "Key": key},
        ExpiresIn=URL_TTL_SECONDS,
    )
