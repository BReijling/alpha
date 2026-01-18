echo ${PACKAGE_NAME}

if ! command -v openapi-generator-cli 2>&1 >/dev/null
then
    echo "The 'openapi-generator-cli' command could not be found"
    echo "Please install it by installing alpha-python with the 'api-generator' extras:"
    echo "eg. 'pip install alpha-python[api-generator]'"
    exit 1
fi

# Validate spec
openapi-generator-cli validate \
    --input-spec ${WORKING_DIR}/${SPEC_FILE}

# Generate code
openapi-generator-cli generate \
    --input-spec ${WORKING_DIR}/${SPEC_FILE} \
    --generator-name ${GENERATOR_NAME} \
    --output ${WORKING_DIR}/api \
    --template-dir ${WORKING_DIR}/templates \
    --package-name ${PACKAGE_NAME} \
    $RESERVED_WORDS_MAPPINGS \
    --additional-properties featureCORS=true \
    --additional-properties languageCode=en \
    --additional-properties servicePackage=${SERVICE_PACKAGE} \
    --additional-properties containerImport="${CONTAINER_IMPORT}" \
    --additional-properties initContainerFrom="${INIT_CONTAINER_FROM}" \
    --additional-properties initContainerFunction="${INIT_CONTAINER_FUNCTION}" \