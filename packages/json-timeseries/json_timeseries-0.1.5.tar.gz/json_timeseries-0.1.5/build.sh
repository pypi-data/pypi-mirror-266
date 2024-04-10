#!/bin/bash

python -m unittest tests/test_json_timeseries.py && python -m build && twine check dist/* && twine upload dist/*
