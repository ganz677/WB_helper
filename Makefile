.PHONY: fmt lint test up down migrate
fmt:
uv run black src
uv run ruff check --fix src
lint:
uv run ruff check src

test:
uv run pytest -q

up:
docker compose -f deploy/docker-compose.yml up --build

down:
docker compose -f deploy/docker-compose.yml down -v

migrate:
docker compose -f deploy/docker-compose.yml exec api bash -lc \
". .venv/bin/activate && alembic -c src/wb_autoanswers/platform/db/migrations/alembic.ini upgrade head"