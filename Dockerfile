FROM python:3.11-slim-bullseye

WORKDIR /app/

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    gcc \
    libc-dev \
    libffi-dev \
    libpq-dev \
    graphviz \
    graphviz-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy project
COPY ./app .

EXPOSE 8000

COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]
