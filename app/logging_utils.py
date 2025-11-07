import os
import json
import uuid
import datetime as dt

import boto3

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
_s3_client = boto3.client("s3")


def log_interaction(
    session_id: str,
    user_message: str,
    bot_response: str,
    meta: dict | None = None,
) -> None:
    """
    Logs each interaction as a separate JSON object in S3.
    One object per message for simplicity.
    """
    if not S3_BUCKET_NAME:
        print("[WARN] S3_BUCKET_NAME not set; skipping S3 logging.")
        return

    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    date_prefix = now[:10]  # YYYY-MM-DD

    key = f"logs/{date_prefix}/{session_id}/{uuid.uuid4().hex}.json"
    payload = {
        "timestamp": now,
        "session_id": session_id,
        "user_message": user_message,
        "bot_response": bot_response,
        "meta": meta or {},
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    _s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=body,
        ContentType="application/json",
    )
    print(f"[INFO] Logged interaction to s3://{S3_BUCKET_NAME}/{key}")