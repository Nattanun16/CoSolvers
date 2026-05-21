FROM python:3.13.12-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN python viable_graph_project/manage.py collectstatic --noinput || true

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python viable_graph_project/manage.py collectstatic --noinput && python viable_graph_project/manage.py runserver 0.0.0.0:8000"]
