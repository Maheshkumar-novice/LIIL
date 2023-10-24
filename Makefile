.DEFAULT_GOAL := req
sources = *.py

.PHONY: install
install:
	pip install -r requirements.txt
	pre-commit install

.PHONY: format
format:
	ruff format . --target-version py311

.PHONY: lint
lint:
	ruff check --fix --exit-non-zero-on-fix .

.PHONY: req
req:
	pip freeze > requirements.txt
