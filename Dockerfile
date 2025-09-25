# Dockerfile

# Base image
FROM python:3.10-slim-bullseye

# Install security updates and essential build tools
RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y --no-install-recommends build-essential && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

# Environment variables
ENV PYTHONUNBUFFERED 1

# Work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project code
COPY . .