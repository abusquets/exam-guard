# abusquets-northwind

To execute any command
```bash
docker-compose exec api bash
```


# Users

## Create admin User
```bash
python manage.py {user_email} {name}
```

# Migrations


```bash
alembic init -t async migrations
```

## Create the initial migration or add a migration
```bash
alembic revision --autogenerate -m "init"

```

```bash

alembic revision --autogenerate -m 'add ts to monitor_data'
alembic revision --autogenerate -m 'add interval to monitors'
alembic revision --autogenerate -m 'add unique constraint monitor_data_monitor_id_ts'
alembic revision --autogenerate -m 'add sku to monitors'


```

## Apply the migrations to the database:

```bash
alembic upgrade head

```

## Undo last migration:

```bash
docker-compose exec api alembic downgrade -1

```

# Populate

```bash
docker-compose up
```

```bash
docker-compose exec api alembic upgrade head
```

```bash
docker-compose exec api python manage.py {user_email} {name}
```
