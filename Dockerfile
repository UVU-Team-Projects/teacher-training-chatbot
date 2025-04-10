FROM python:3.12-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Don't use the CMD that runs the app - we want an interactive shell for development
WORKDIR /workspace

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the application
CMD ["streamlit", "run", "src/web/web.py"]