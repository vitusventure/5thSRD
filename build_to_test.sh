#!/bin/bash

git pull

python3 build_indexes.py

mkdocs build --clean

aws s3 sync ./site/ s3://5thsrd.org-test/ --region="us-east-1" --delete
