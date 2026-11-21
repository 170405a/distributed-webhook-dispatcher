
from fastapi import FastAPI, status, Depends
from pydantic import BaseModel, HttpUrl
from typing import Any
from uuid import uuid4
from sqlalchemy.orm import Session
import threading
import time

from database import get_db, engine
from models import Base, WebhookJob


app = FastAPI()


# Background worker function
def run_background_worker():

    from worker import process_pending_jobs

    print("Background worker started!")

    while True:
        try:
            process_pending_jobs()

        except Exception as error:
            print(f"Worker error: {error}")

        time.sleep(2)


# Create database tables and start worker
@app.on_event("startup")
def create_tables():

    Base.metadata.create_all(bind=engine)

    threading.Thread(
        target=run_background_worker,
        daemon=True
    ).start()


# Webhook request structure
class WebhookRequest(BaseModel):
    destinationUrl: HttpUrl
    eventId: str
    payload: dict[str, Any]


# Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to Webhook Dispatcher"
    }


# Webhook dispatch endpoint
@app.post(
    "/api/webhooks/dispatch",
    status_code=status.HTTP_202_ACCEPTED
)
def dispatch_webhook(
    request: WebhookRequest,
    db: Session = Depends(get_db)
):

    job_id = f"job_{uuid4().hex[:8]}"

    new_job = WebhookJob(
        job_id=job_id,
        event_id=request.eventId,
        destination_url=str(request.destinationUrl),
        payload=request.payload,
        status="pending",
        attempts=0
    )

    db.add(new_job)
    db.commit()

    return {
        "status": "queued",
        "jobId": job_id
    }
