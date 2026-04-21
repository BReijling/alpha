#!/bin/bash

echo "Starting server on port ${PORT}..."
python ${API_LOCATION}/${PACKAGE_NAME}/__main__.py --port ${PORT}
