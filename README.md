
# Distributed Webhook Dispatcher

A Python-based backend application that accepts webhook events, stores them in PostgreSQL, and delivers them to destination servers using a background worker.

## Features

- FastAPI-based webhook ingestion API
- PostgreSQL database integration
- Background webhook processing
- HTTP POST delivery using HTTPX
- Automatic retries with exponential backoff
- Delivery attempt logging
- Per-destination rate limiting

## Technologies Used

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- HTTPX
- Pydantic

## Project Structure

```text
webhook-dispatcher/
│
├── main.py
├── database.py
├── models.py
├── worker.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project folder:

```env
DATABASE_URL=your_postgresql_connection_string
```

5. Create the PostgreSQL database and required tables.

## Run the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

Run the background worker in a separate terminal:

```bash
python worker.py
```

## API Endpoint

**POST** `/api/webhooks/dispatch`

Example request:

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

Example response:

```json
{
  "status": "queued",
  "jobId": "job_generated_id"
}
```

HTTP Status: `202 Accepted`

## Retry Mechanism

The worker supports up to four delivery attempts:

- Initial attempt
- First retry after 2 seconds
- Second retry after 4 seconds
- Third retry after 8 seconds

Retries are performed for server errors, HTTP 429 responses, and request failures.

## Rate Limiting

A sliding-window rate limiter restricts delivery to a maximum of five requests per second per destination within a single worker process.

## License

This project is developed for educational and internship assignment purposes.
