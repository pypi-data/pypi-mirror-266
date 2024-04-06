#!/usr/bin/env bash
set -e

datamodel-codegen \
    --use-default-kwarg \
    --input sm-skill-api-definition/apis/openapi/ \
    --input-file-type openapi \
    --output src/smskillsdk/models/
