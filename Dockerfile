FROM python:3.10-slim-bullseye

RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y --no-install-recommends build-essential && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*


ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt


COPY . .
