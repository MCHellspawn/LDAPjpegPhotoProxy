FROM python:3-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN mkdir /app
WORKDIR /app

# Install pip requirements
COPY requirements.txt /app
RUN python -m pip install -r /app/requirements.txt

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

COPY LDAPjpegPhotoProxy.py /app
RUN mkdir config
COPY config/config-example.ini /app/config/config.ini
CMD ["sh", "-c", "python3 LDAPjpegPhotoProxy.py"]