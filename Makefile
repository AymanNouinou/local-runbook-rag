.PHONY: install test run

install:
	python3 -m pip install -e '.[dev]'

test:
	pytest

run:
	uvicorn app.main:app --reload
