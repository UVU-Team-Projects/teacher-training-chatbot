FROM python:3.12-slim

# Install necessary packages and setup for Python
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    wget \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set up a working directory
WORKDIR /workspace

# Install Python dependencies
COPY requirements.txt* .
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; fi

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Add port for Ollama API
EXPOSE 11434
