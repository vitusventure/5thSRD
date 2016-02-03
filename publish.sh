#!/bin/bash

# Get the latest changes
git pull

# Generate Offline spell lists
python generate_linked_spell_lists.py --offline
python generate_spell_indexes.py --offline

# Build the offline site
mkdocs build --clean --config-file offline_build_config.yml

# Generate spell lists
python generate_linked_spell_lists.py
python generate_spell_indexes.py

# Build the site
mkdocs build --clean

# Zip the offline version
rm /tmp/5thsrd_offline.zip
zip -r /tmp/5thsrd_offline.zip 5thsrd_offline/
mv /tmp/5thsrd_offline.zip ./site/

# Sync to S3
aws s3 sync ./site/ s3://5thsrd.org/ --region="us-east-1"

# Invalidate Cloudfront cache
aws cloudfront create-invalidation --distribution-id E21QCV3S5T8Z34 --paths "/*"
