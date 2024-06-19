# Use the official Airflow image as base
FROM apache/airflow:2.7.1-python3.9

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements file
COPY requirements.txt /opt/airflow/

# Switch to root user for system dependencies
USER root

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install Python dependencies
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Set working directory
WORKDIR /opt/airflow

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/health || exit 1
