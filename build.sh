#!/bin/bash python3

rm -rf dist build video2live.egg-info

python setup.py sdist bdist_wheel

twine upload dist/*
