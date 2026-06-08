#!/bin/bash
set -e

PG_DATA="/var/lib/postgresql/data/app-db"
PG_HBA="/var/lib/postgresql/data/app-db/pg_hba.conf"

mkdir -p /var/run/postgresql
chown postgres:postgres /var/run/postgresql

if [ ! -d "$PG_DATA/base" ]; then
    mkdir -p "$PG_DATA"
    chown postgres:postgres "$PG_DATA"
    su postgres -c "initdb -D $PG_DATA"
    
    echo "local all all trust" > "$PG_HBA"
    echo "host all all 127.0.0.1/32 trust" >> "$PG_HBA"
    echo "host all all ::1/128 trust" >> "$PG_HBA"
    chown postgres:postgres "$PG_HBA"
fi

su postgres -c "postgres -D $PG_DATA -c listen_addresses='localhost' -c port=5432 -c unix_socket_directories='/var/run/postgresql' &"

sleep 5

if ! su postgres -c "psql -lqt 2>/dev/null | cut -d '|' -f 1 | grep -qw $DB_NAME"; then
    su postgres -c "createdb -U postgres $DB_NAME"
    su postgres -c "psql -U postgres -d $DB_NAME -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';\""
    su postgres -c "psql -U postgres -d $DB_NAME -c \"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;\""
    su postgres -c "psql -U postgres -d $DB_NAME -c \"GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;\""
    su postgres -c "psql -U postgres -d $DB_NAME -c \"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;\""
fi

cd /app

python manage.py migrate --noinput

python manage.py seed_users

python manage.py runserver 0.0.0.0:8000