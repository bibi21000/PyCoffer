#!/usr/bin/make -f
-include Makefile.local

ifndef PYTHON
PYTHON:=python3
endif

.PHONY: venv tests

clean:
	rm -rf build extract_tar extract_tar_
	rm -rf .pytest_cache .ruff_cache
	rm -f pycoffer_static.bin

venv:
	${PYTHON} -m venv venv
	./venv/bin/pip install -e .
	./venv/bin/pip install .[test]
	./venv/bin/pip install .[cli]
	./venv/bin/pip install .[fido]
	./venv/bin/pip install .[build]
	./venv/bin/pip install .[doc]
	./venv/bin/pip install ../FernetFile -e .
	./venv/bin/pip install ../NaclFile -e .
	./venv/bin/pip install ../AesFile -e .
	./venv/bin/pip install ../CofferFile -e .

venv_nuitka:
	python3 -m venv venv_nuitka
	./venv_nuitka/bin/pip install --upgrade pip
	./venv_nuitka/bin/pip install -e .
	./venv_nuitka/bin/pip install -e .[cli]
	./venv_nuitka/bin/pip install -e .[binaries]
	./venv_nuitka/bin/pip install -e ../FernetFile
	./venv_nuitka/bin/pip install -e ../AeslFile
	./venv_nuitka/bin/pip install -e ../NaclFile
	./venv_nuitka/bin/pip install -e ../CofferFile

pycoffer_static.bin: venv_nuitka
#~ 	./venv_nuitka/bin/nuitka --show-progress --remove-output --include-package=pycoffer --include-package=cofferfile --include-package=fernetfile --include-package=naclfile --onefile ./venv_nuitka/bin/pycoffer --output-dir=
	./venv_nuitka/bin/nuitka --include-distribution-metadata=pycoffer --include-distribution-metadata=cofferfile --include-distribution-metadata=aesfile --include-distribution-metadata=naclfile --remove-output --onefile ./venv_nuitka/bin/pycoffer_static --output-dir=

build:
	rm -rf dist
	./venv/bin/python3 -m build

testpypi:
	./venv/bin/python3 -m twine upload --repository testpypi --verbose dist/*

apidoc:
	./venv/bin/sphinx-apidoc --output-dir docs/api --force pycoffer
	git checkout docs/api/modules.rst

doc:
	cd docs && make html

pypi:
	./venv/bin/python3 -m twine upload --repository pypi --verbose dist/*

ruff:
	./venv/bin/ruff check pycoffer/

bandit:
	./venv/bin/bandit -r pycoffer

tests:
	./venv/bin/pytest  --random-order -n auto --ignore=tests/test_benchmark.py tests/

benchmark:
	./venv/bin/pip install .[benchmark]
	./venv/bin/pytest tests/test_benchmark.py
