#!/usr/bin/make -f
.PHONY: venv tests

venv:
	python3 -m venv venv
	./venv/bin/pip install .
	./venv/bin/pip install .[test]
	./venv/bin/pip install .[zstd]
	./venv/bin/pip install .[store]

build:
	rm -rf dist
	./venv/bin/python3 -m build

testpypi:
	./venv/bin/python3 -m twine upload --repository testpypi --verbose dist/*

doc:
	./venv/bin/pdoc --output-directory docs fernetfile/zstd.py fernetfile/store.py fernetfile/__init__.py

pypi:
	./venv/bin/python3 -m twine upload --repository pypi --verbose dist/*

ruff:
	./venv/bin/ruff check fernetfile/

bandit:
	./venv/bin/bandit -r fernetfile

tests:
	./venv/bin/pytest  --random-order -n auto --ignore=tests/test_benchmark.py tests/

benchmark:
	./venv/bin/pytest tests/test_benchmark.py
