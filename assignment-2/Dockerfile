FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY tests/ ./tests/

ENV PYTHONPATH=/app
ENV DATABASE_PATH=/app/data/aceest_fitness.db
ENV PORT=5000

RUN mkdir -p /app/data

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
