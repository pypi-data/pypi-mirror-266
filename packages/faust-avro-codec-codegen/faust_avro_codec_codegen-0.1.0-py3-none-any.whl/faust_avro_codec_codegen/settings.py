from pathlib import Path

import tomlkit
from pydantic import BaseModel


class ConfigNotFoundError(Exception):
    pass


class Settings(BaseModel):
    schema_dir: Path = Path("schemas")
    outfile: Path = Path("models.py")
    faust_app_models_module: str = "models"
    faust_app_module: str = "app:app"
    faust_settings_module = "settings"

    @classmethod
    def from_toml(cls) -> "Settings":
        pyproject_toml = Path("pyproject.toml")
        standalone_toml = Path("faust_avro_code_gen.toml")
        if cls.pyproject_config_exists(pyproject_toml):
            return cls(
                **tomlkit.loads(pyproject_toml.read_bytes())["tool"][
                    "faust_avro_codec_codegen"
                ]
            )
        if standalone_toml.exists():
            return cls(**tomlkit.loads(standalone_toml.read_bytes()).unwrap())
        raise ConfigNotFoundError("Please provide a configuration in a pyproject.toml under [tools.faust_avro_codec_codegen] or faust_avro_codec_codegen.toml file.")

    @classmethod
    def pyproject_config_exists(cls, pyproject_toml: Path) -> bool:
        return (
            pyproject_toml.exists()
            and tomlkit.loads(pyproject_toml.read_bytes())
            .get("tool", {})
            .get("faust_avro_codec_codegen")
            is not None
        )
