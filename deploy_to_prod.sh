#!/bin/bash

# Get the latest changes
git pull

# Generate offline indexes
python3 build_indexes.py --offline

# Build the offline site
mkdocs build --clean --config-file offline_build_config.yml

# Generate regular indexes
python3 build_indexes.py

# Build the site
mkdocs build --clean

# Zip the offline version
rm /tmp/5thsrd_offline.zip
zip -r /tmp/5thsrd_offline.zip 5thsrd_offline/
mv /tmp/5thsrd_offline.zip ./site/

# Sync to S3
aws s3 sync ./site/ s3://5thsrd.org/ --region="us-east-1" --delete

# Set Cache-Control on static resources
s3cmd modify --recursive s3://5thsrd.org/css/ --add-header=Cache-Control:max-age=604800 -v
s3cmd modify --recursive s3://5thsrd.org/js/ --add-header=Cache-Control:max-age=604800 -v
s3cmd modify --recursive s3://5thsrd.org/img/ --add-header=Cache-Control:max-age=604800 -v
s3cmd modify --recursive s3://5thsrd.org/fonts/ --add-header=Cache-Control:max-age=604800 -v
