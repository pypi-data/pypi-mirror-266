.PHONY = lint test

default: lint test coverage

lint:
	flake8 src/pyrecipes tests

test:
	coverage run

coverage:
	coverage report

pip-install:
	pip install pip-tools
	pip-compile
	pip-sync
