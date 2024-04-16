coffee:
	@printf 'Enjoy your coffee! ☕️\n'

build:
	@docker compose build

run:
	@docker compose up

restart:
	@docker-compose stop
	@docker-compose up --no-deps

background:
	@docker compose up -d

debugpy:
	@DEBUGPY=True docker compose up

load_data:
	@docker compose exec api python fixtures/load_master_data.py
	@docker compose exec api python fixtures/load_monitor_data.py

load_fixtures:
	@docker compose exec api python fixtures/load_monitor_data.py

stop:
	@docker compose down

shell:
	@docker compose exec api bash

logs:
	@docker compose logs -f

makemigrations:
	@docker compose run api alembic revision --autogenerate -m "$(m)"

migrate:
	@docker compose run api alembic upgrade head

unmigrate:
	@docker-compose run api alembic downgrade -1

destroy:
	@docker-compose down -v

all: build
	@LOADFIXTURES=True docker compose up

tests:
	@docker-compose run api pytest -x --no-cov


.PHONY: coffee build run load_fixtures stop shell tests
