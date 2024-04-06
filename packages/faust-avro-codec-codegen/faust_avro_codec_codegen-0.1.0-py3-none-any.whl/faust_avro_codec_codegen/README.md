# TODO: UPDATE THIS

# CODE GEN

This code generator approach generates "full" Python models that preserves 
`doc` and `default` attributes from the Avro schema. Example data, in an 
`example` tag included at the top level of the schema, is also preserved.

All `avsc` files in the `avro` directory are processed and the generated code
is written to `sustainability_service/faust_app/models.py`.

## WARNINGS

This code generator is not complete. It does not handle all Avro types. If 
an unhandled type is encountered, the code generator will raise an exception 
and DIE. You will need to modify the `match` statement in 
`avro_code_gen/main.py:convert_avro_field_to_python` to handle the new type.

## Configuration

Modify `SCHEMA_DIR` in `avro_code_gen/main.py` to search for AVRO schema 
files in a different directory.

Modify `OUTPUT_FILE` in `avro_code_gen/main.py` to write the generated code
to a different file.

## Usage

```bash
poetry run python -m avro_code_gen
```

## Verification

There is a provided test that verifies the generated code. Run it with:

```bash
poetry run python verify_schemas.py
```
