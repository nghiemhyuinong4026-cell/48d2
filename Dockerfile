FROM postgres:15-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DB_NAME=capa_system
ENV DB_USER=capa_user
ENV DB_PASSWORD=capa_password
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DJANGO_SECRET_KEY=dev-secret-key-change-in-production
ENV DEBUG=True

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /var/lib/postgresql/data/app-db
RUN chown postgres:postgres /var/lib/postgresql/data/app-db

RUN git init && git config user.email "docker@local" && git config user.name "Docker" && git add . && git commit -m "Initial commit"

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]