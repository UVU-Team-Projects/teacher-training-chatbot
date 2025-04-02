FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (including PostgreSQL client and build essentials)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional packages that might be missing
RUN pip install --no-cache-dir \
    psycopg2-binary \
    streamlit \
    langchain-ollama \
    langchain-core \
    sqlalchemy

# Copy the rest of the application
COPY . .

# Make sure the entrypoint script is executable
RUN chmod +x /app/docker-entrypoint.sh

# Set the entrypoint to run the application
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["streamlit", "run", "src/web/web.py", "--server.port=8501", "--server.address=0.0.0.0"]
