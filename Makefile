#!/usr/bin/make -f
-include makefile.local

ifndef PYTHON
PYTHON:=python3
endif

.PHONY: venv tests

venv:
	${PYTHON} -m venv venv
	./venv/bin/pip install .
	./venv/bin/pip install .[test]
	./venv/bin/pip install .[cli]
	./venv/bin/pip install .[store]
	./venv/bin/pip install .[build]
	./venv/bin/pip install .[doc]
	./venv/bin/pip install ../FernetFile -e .
	./venv/bin/pip install ../NaclFile -e .
	./venv/bin/pip install ../CofferFile -e .

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
#~ 	./venv/bin/pip install .[benchmark]
	./venv/bin/pytest tests/test_benchmark.py
