FROM python:3.11-slim

WORKDIR /app
COPY backend /app/backend
COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --no-cache-dir -r backend/requirements.txt

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["python","-m","uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"]

