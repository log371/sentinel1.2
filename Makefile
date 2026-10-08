.PHONY: install test lint run demo

install:
	python -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check .

run:
	uvicorn sentinelia.main:app --reload

demo:
	./scripts/demo.sh

