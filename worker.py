
import httpx
import time
from collections import defaultdict, deque

from database import SessionLocal
from models import WebhookJob, WebhookAttempt


# Rate limiter: separate request history for each destination
request_times = defaultdict(deque)


def apply_rate_limit(destination_url):

    timestamps = request_times[destination_url]

    while True:

        current_time = time.monotonic()

        # Remove requests older than 1 second
        while timestamps and current_time - timestamps[0] >= 1:
            timestamps.popleft()

        # Allow maximum 5 requests per second
        if len(timestamps) < 5:
            timestamps.append(time.monotonic())
            break

        # Wait until an old request leaves the window
        wait_time = 1 - (current_time - timestamps[0])

        print(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
        time.sleep(max(wait_time, 0))


def process_pending_jobs():

    db = SessionLocal()

    try:
        jobs = db.query(WebhookJob).filter(
            WebhookJob.status == "pending"
        ).all()

        for job in jobs:

            for attempt in range(1, 5):

                http_code = None
                error_message = None
                should_retry = False

                try:
                    # Apply rate limit before every request
                    apply_rate_limit(job.destination_url)

                    print(f"Job {job.job_id}: Attempt {attempt}")

                    response = httpx.post(
                        job.destination_url,
                        json=job.payload,
                        timeout=10
                    )

                    http_code = response.status_code
                    response.raise_for_status()

                    job.status = "success"
                    print(f"Job {job.job_id} delivered successfully!")

                except httpx.HTTPStatusError as error:

                    http_code = error.response.status_code
                    error_message = str(error)

                    print(f"HTTP error: {http_code}")

                    if http_code == 429 or http_code >= 500:
                        should_retry = True

                except (httpx.TimeoutException, httpx.RequestError) as error:

                    error_message = str(error)
                    should_retry = True

                    print(f"Request failed: {error}")

                # Update attempt count
                job.attempts = attempt

                # Save attempt details
                attempt_log = WebhookAttempt(
                    job_id=job.job_id,
                    event_id=job.event_id,
                    attempt_number=attempt,
                    status="success" if job.status == "success" else "failed",
                    http_status_code=http_code,
                    error_message=error_message
                )

                db.add(attempt_log)
                db.commit()

                if job.status == "success":
                    break

                if not should_retry:
                    job.status = "failed"
                    db.commit()
                    break

                if attempt == 4:
                    job.status = "failed"
                    print(f"Job {job.job_id} failed after 4 attempts.")
                    db.commit()
                    break

                delay = 2 ** attempt

                print(f"Retrying after {delay} seconds...")
                time.sleep(delay)

    finally:
        db.close()


if __name__ == "__main__":
    process_pending_jobs()
