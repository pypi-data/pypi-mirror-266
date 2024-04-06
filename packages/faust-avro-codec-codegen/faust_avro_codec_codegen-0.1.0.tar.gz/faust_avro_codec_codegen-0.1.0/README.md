# README
## WARNING THIS LIB IS INCOMPLETE.

## Faust Avro Codec Codegen

This project is a Python-based code generator that creates Faust topics and codecs from Avro schemas. It is dependent on `faust-avro-model-codegen`.

### Prerequisites

- Python 3.10 or higher
- Faust
- Avro
- pydantic
- faust-avro-model-codegen


### Installation

Clone the repository:

```bash
git clone https://github.com/bboggs-streambit/faust_avro_codec_codegen.git
```

Navigate to the project directory:

```bash
cd faust_avro_codec_codegen
```

Install the required dependencies:

```bash
poetry install
```

### Configuration

The configuration for the code generator is done via a TOML file. You can either use a `pyproject.toml` file under the `[tool.faust_avro_codec_codegen]` section or a standalone `faust_avro_code_gen.toml` file.

Here is an example configuration:

```toml
[tool.faust_avro_codec_codegen]
schema_dir = "schemas"
outfile = "models.py"
faust_app_models_module = "models"
faust_app_module = "app:app"
faust_settings_module = "settings"
```

### Usage

To generate the Faust topics and codecs, run the `__main__.py` script:

```bash
python -m faust_avro_codec_codegen
```

This will generate the Faust topics and codecs based on the Avro schemas in the directory specified in the configuration file. The generated code will be written to the output file specified in the configuration file.

### Contributing

Contributions are welcome. Please submit a pull request.

### License

This project is licensed under the MIT License.