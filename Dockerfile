FROM python:alpine

WORKDIR /app

COPY requirements.txt .


# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    postgresql-dev \
    build-base \
    linux-headers \
    git \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps  # Remove build deps to reduce image size

COPY . .

ENV PYTHONPATH=/app

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]