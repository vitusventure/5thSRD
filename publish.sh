#!/bin/bash

# Get the latest changes
git pull

# Build the site
mkdocs build --theme=readable --clean

# Sync to S3
s3cmd sync site/ s3://5thsrd.org/
