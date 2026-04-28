FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (e.g. for PostgreSQL client, reportlab fonts, etc)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize the db before starting (optional, for simple sqlite cases)
# RUN python -c "from app import db, app; app.app_context().push(); db.create_all()"

EXPOSE 5000

# Production ready server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "3", "app:app"]
