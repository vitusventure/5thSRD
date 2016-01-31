#!/bin/bash

# Get the latest changes
git pull

# Generate spell lists
python generate_linked_spell_lists.py
python generate_spell_indexes.py

# Build the site
mkdocs build --clean

# Sync to S3
aws s3 sync ./site/ s3://5thsrd.org/ --region="us-east-1"

# Invalidate Cloudfront cache
aws cloudfront create-invalidation --distribution-id E21QCV3S5T8Z34 --paths "/*"
