FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

RUN export PYTHONPATH=$PYTHONPATH:$(pwd)
# Keep container running for development
# CMD ["tail", "-f", "/dev/null"] 