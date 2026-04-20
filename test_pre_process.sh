#!/bin/sh

alpha api gen \
    --spec-file tests/openapi/specification/openapi.yaml \
    --api-package alpha_test_api \
    --service-package alpha \
    --container-import "from alpha.utils.openapi_test.container import Container" \
    --init-container-from alpha.utils.openapi_test.container \
    --init-container-function init_container \
    --no-watch

cp api/alpha_test_api/__main__.py api/alpha_test_api/_app.py

uv pip install -e api
pip install -e api
