#!/bin/bash
[ -f pycoffer_static.bin ] && exit
python3 -m venv venv_static
./venv_static/bin/pip install --upgrade pip
./venv_static/bin/pip install -e .
./venv_static/bin/pip install -e .[cli]
./venv_static/bin/pip install -e .[binaries]
./venv_static/bin/nuitka --remove-output --onefile \
    --include-package=pycoffer \
    --include-distribution-metadata=pycoffer \
    --include-distribution-metadata=cofferfile \
    --include-distribution-metadata=fernetfile \
    --include-distribution-metadata=naclfile \
    ./venv_static/bin/pycoffer_static --output-dir=
