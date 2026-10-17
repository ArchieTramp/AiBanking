.PHONY: test lint migrate

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .

migrate:
	uv run alembic upgrade head