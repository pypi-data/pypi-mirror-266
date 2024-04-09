# -*- coding: utf-8 -*-
import jsonschema
from r3xa.utils import get_schema


def validate(instance):
    schema = get_schema()

    validator = jsonschema.validators.Draft202012Validator(schema)

    errors = sorted(validator.iter_errors(instance), key=jsonschema.exceptions.relevance)

    if not len(errors):
        print("Valid json file")
        return

    error_message = "\n - ".join([e.message for e in errors])
    raise jsonschema.exceptions.ValidationError(f"JSON is not valid: \n - {error_message}")
