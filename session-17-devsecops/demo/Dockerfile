FROM python:3.12-alpine@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4

WORKDIR /app

COPY requirements.txt .

RUN apk upgrade --no-cache \
    && pip install --no-cache-dir -r requirements.txt \
    && adduser -D -u 10001 appuser

COPY app ./app

EXPOSE 5001
USER 10001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--access-logfile", "-", "app.app:app"]
