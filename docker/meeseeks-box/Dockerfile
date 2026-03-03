FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the Meeseeks stack
COPY skills/meeseeks/ /app/skills/meeseeks/
COPY the-crypt/ /app/the-crypt/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/the-crypt/ancestors \
    /app/the-crypt/meta \
    /app/logs

# Expose ports
EXPOSE 8080 9090

# Entry point
ENTRYPOINT ["python", "-m", "skills.meeseeks.box_server"]
