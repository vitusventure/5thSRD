#!/bin/bash

# Get the latest changes
git pull

# Generate offline indexes
poetry run python ./build_indexes.py --offline

# Build the offline site
poetry run mkdocs build --clean --config-file offline_build_config.yml

# Generate regular indexes
poetry run python ./build_indexes.py

# Build the site
poetry run mkdocs build --clean

# Zip the offline version
rm /tmp/5thsrd_offline.zip
zip -r /tmp/5thsrd_offline.zip 5thsrd_offline/
mv /tmp/5thsrd_offline.zip ./site/

# Sync to S3
aws s3 sync ./site/ s3://5thsrd.org/ --region="us-east-1" --delete
