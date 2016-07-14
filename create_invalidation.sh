#!/bin/bash

# Invalidate Cloudfront cache
aws cloudfront create-invalidation --distribution-id E21QCV3S5T8Z34 --paths "/*" --output json
