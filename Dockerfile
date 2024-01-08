FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED 1

# Update and install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgdal-dev gcc g++ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN useradd -m -s /bin/bash myuser
USER myuser

WORKDIR /home/myuser/code

# Copy the requirements.txt first to leverage Docker cache
COPY --chown=myuser:myuser requirements.txt /home/myuser/code/

# Install Python packages from requirements.txt
RUN pip install --user --upgrade pip && \
    pip install --user -r requirements.txt

COPY --chown=myuser:myuser . /home/myuser/code/
