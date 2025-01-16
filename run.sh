#!/bin/bash

VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate

pip install --upgrade pip
pip install spot

export PYTHONPATH=$HOME/usr/lib/python3.12/site-packages:$PYTHONPATH

python3 hoa_parser.py

deactivate
