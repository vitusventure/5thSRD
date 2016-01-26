#!/bin/bash

# Get the latest changes
git pull

# Generate spell lists
python generate_linked_spell_lists.py
python generate_spell_indexes.py

# Build the site
mkdocs build --clean

# Sync to S3
s3cmd sync site/ s3://5thsrd.org/
