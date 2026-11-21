# Distributed Webhook Dispatcher

A Python-based backend application that accepts webhook events, stores them in PostgreSQL, and delivers them asynchronously using a background worker.

## Live Demo

- **Live API:** https://distributed-webhook-dispatcher-6ria.onrender.com
- **API Documentation:** https://distributed-webhook-dispatcher-6ria.onrender.com/docs
- **GitHub Repository:** https://github.com/170405a/distributed-webhook-dispatcher

## Features

- Webhook ingestion using FastAPI.
- Request validation using Pydantic.
- Immediate HTTP 202 Accepted response.
- PostgreSQL database integration.
- Automatic background job processing.
- HTTP POST delivery using HTTPX.
- Automatic retry mechanism with exponential backoff.
- Maximum 4 delivery attempts (1 initial + 3 retries).
- Retry delays of 2, 4 and 8 seconds.
- Attempt logging in PostgreSQL.
- Per-destination sliding-window rate limiting (5 requests per second).

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- HTTPX
- Pydantic
- Git and GitHub
- Render

## Project Structure

```text
webhook-dispatcher/
│
├── main.py
├── worker.py
├── database.py
├── models.py
├── requirements.txt
├── README.md
└── .gitignore
```

## API Endpoint

**POST** `/api/webhooks/dispatch`

### Sample Request

```json
{
  "destinationUrl": "https://httpbin.org/post",
  "eventId": "evt_123456",
  "payload": {
    "event": "user.signup",
    "userId": "usr_999"
  }
}
```

### Successful Response

HTTP Status: `202 Accepted`

```json
{
  "status": "queued",
  "jobId": "job_12345678"
}
```

## Retry Mechanism

The application retries failed webhook deliveries for:
- HTTP 429 responses.
- HTTP 5xx responses.
- Request timeouts.
- Network connection errors.

Maximum attempts: 4.

Retry delays:
- First retry: 2 seconds.
- Second retry: 4 seconds.
- Third retry: 8 seconds.

Jobs are marked as successful or failed after processing.

## Rate Limiting

A sliding-window rate limiter controls requests separately for each destination URL.

Maximum allowed rate: 5 requests per second per destination.

The current implementation maintains rate-limit history in application memory and is intended for a single worker process.

## Database Tables

### webhook_jobs

Stores webhook jobs, destination URLs, payloads, status, and attempt count.

### webhook_attempts

Stores individual delivery attempts, including event ID, attempt number, status, HTTP response code, error details, and timestamp.

Tables are automatically created when the FastAPI application starts.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/170405a/distributed-webhook-dispatcher.git
cd distributed-webhook-dispatcher
```

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variable

Create a `.env` file in the project directory:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/webhook_dispatcher
```

Replace the credentials with your PostgreSQL details.

### 5. Start the application

```bash
uvicorn main:app --reload
```

The background worker starts automatically with the FastAPI application.

### 6. Open API documentation

```text
http://127.0.0.1:8000/docs
```

## Deployment

The application is deployed on Render using:
- Render Web Service for FastAPI and its background worker thread.
- Render PostgreSQL for persistent job and attempt storage.

Configure the `DATABASE_URL` environment variable in Render.

## Testing

The application was tested for:

- Webhook ingestion and HTTP 202 response.
- PostgreSQL job storage.
- Automatic background processing.
- Successful webhook delivery.
- Retry handling with exponential backoff.
- Logging of all four delivery attempts.
- Rate limiter implementation.

## Important Note

The current deployment uses a background thread within the web service and an in-memory rate limiter. It is designed as a simple internship assignment implementation rather than a multi-instance distributed production system.

Render's free web service may spin down during inactivity.
