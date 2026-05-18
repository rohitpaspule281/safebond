FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip

COPY backend/requirements.txt /app/backend/requirements.txt
COPY backend/pyproject.toml /app/backend/pyproject.toml
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
RUN pip install --no-cache-dir -e /app/backend

WORKDIR /app/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
