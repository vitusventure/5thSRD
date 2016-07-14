#!/bin/bash

git pull

mkdocs build --clean

aws s3 sync ./site/ s3://5thsrd.org-test/ --region="us-east-1"
