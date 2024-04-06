import pathlib

import jinja2
from faust_avro_model_codegen import AvroSchemaDirectoryParser, TemplateWriter
from faust_avro_model_codegen.template_writer import RenderedTemplate
from rich import print

from faust_avro_codec_codegen.settings import Settings

loader = jinja2.FileSystemLoader(searchpath=pathlib.Path(__file__).parent / "templates")
tpls = jinja2.Environment(loader=loader)


def main() -> None:
    settings = Settings.from_toml()
    schemas = list(AvroSchemaDirectoryParser.parse_dir(settings.schema_dir))
    print(f"\n[italic blue]Generating Faust Topics and Codecs at {settings.outfile}...[/]")
    codec_tpl_file = tpls.get_template("topics.py.jinja2")
    rendered = codec_tpl_file.render(
        models_module=settings.faust_app_models_module,
        faust_app_module=settings.faust_app_module.split(":")[0],
        faust_app_name=settings.faust_app_module.split(":")[1],
        faust_settings_module=settings.faust_settings_module,
        schemas=schemas,
        __name__="faust_avro_codecs_codegen",
    )
    TemplateWriter().write(settings.outfile, RenderedTemplate(rendered))
    print(f"[italic green]Faust topics and codecs generated successfully![/]")
