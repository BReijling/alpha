#!/bin/bash

if ! pip show "connexion" > /dev/null 2>&1
then
  echo "The 'connexion' package is not installed."
  echo "Please install it by installing alpha-python with the 'flask' extras:"
  echo "eg. 'pip install alpha-python[flask]'"
  exit 1
fi

echo "Starting server on port ${PORT}..."
python ${API_LOCATION}/${PACKAGE_NAME}/__main__.py --port ${PORT}
