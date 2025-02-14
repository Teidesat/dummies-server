FROM ubuntu:noble

# Install system dependencies
RUN apt update \
    && apt install -y \
        python3 \
        python3-pip \
    && apt clean

# Install python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --break-system-packages --no-cache-dir --requirement /tmp/requirements.txt
