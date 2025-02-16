#!/usr/bin/make -f
-include Makefile.local

ifndef PYTHON
PYTHON:=python3
endif

.PHONY: venv tests

venv:
	${PYTHON} -m venv venv
	./venv/bin/pip install -e .
	./venv/bin/pip install .[test]
	./venv/bin/pip install .[cli]
	./venv/bin/pip install .[build]
	./venv/bin/pip install .[doc]
	./venv/bin/pip install ../FernetFile -e .
	./venv/bin/pip install ../NaclFile -e .
	./venv/bin/pip install ../CofferFile -e .

venv_nuitka:
	python3 -m venv venv_nuitka
	./venv_nuitka/bin/pip install --upgrade pip
	./venv_nuitka/bin/pip install -e .
	./venv_nuitka/bin/pip install -e .[test]
	./venv_nuitka/bin/pip install -e .[cli]
	./venv_nuitka/bin/pip install -e .[binaries]
	./venv_nuitka/bin/pip install -e ../FernetFile
	./venv_nuitka/bin/pip install -e ../NaclFile
	./venv_nuitka/bin/pip install -e ../CofferFile

pycoffer.bin: venv_nuitka
	./venv_nuitka/bin/nuitka --remove-output --include-package-data=pycoffer --include-package=pycoffer --include-package=cofferfile --include-package=fernetfile --include-package=naclfile --onefile ./venv_nuitka/bin/pycoffer --output-dir=

build:
	rm -rf dist
	./venv/bin/python3 -m build

testpypi:
	./venv/bin/python3 -m twine upload --repository testpypi --verbose dist/*

apidoc:
	./venv/bin/sphinx-apidoc --output-dir docs/source/api --force pycoffer

doc:
	./venv/bin/pdoc --output-directory docs pycoffer/zstd.py pycoffer/store.py pycoffer/__init__.py

pypi:
	./venv/bin/python3 -m twine upload --repository pypi --verbose dist/*

ruff:
	./venv/bin/ruff check pycoffer/

bandit:
	./venv/bin/bandit -r pycoffer

tests:
	./venv/bin/pytest  --random-order -n auto --ignore=tests/test_benchmark.py tests/

benchmark:
#~ 	./venv/bin/pip install .[benchmark]
	./venv/bin/pytest tests/test_benchmark.py
