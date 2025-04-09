FROM python:3.12-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Don't use the CMD that runs the app - we want an interactive shell for development
WORKDIR /workspace

# We'll install requirements in postCreateCommand instead
