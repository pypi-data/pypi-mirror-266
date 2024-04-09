import typer
from typing_extensions import Annotated

from cff2toml.cli.command_metadata_output import CommandMetadataOutput
from cff2toml.cli.context_helpers import is_json_output, is_verbose_output
from cff2toml.models.files.cff_file import DEFAULT_CITATION_CFF_FILE_PATH
from cff2toml.models.files.pyproject_toml_file import DEFAULT_PYPROJECT_TOML_FILE_PATH

from rich import print, print_json

app_view = typer.Typer(no_args_is_help=True)


def _view_metadata(ctx: typer.Context, common_metadata_name: str, cff_file_path: str, pyproject_toml_file_path: str):

    output: CommandMetadataOutput = CommandMetadataOutput(
        command="view",
        common_metadata_name=common_metadata_name,
        cff_file_path=cff_file_path,
        pyproject_toml_file_path=pyproject_toml_file_path)
    output.setup()

    if not is_json_output(ctx):
        if is_verbose_output(ctx):
            print(
                f"[yellow]viewing {output.common_metadata_name} metadata...[/yellow]")
            print(
                f"{output.cff_file_path} has {output.cff_file_metadata_name} [green]{output.cff_file_metadata_value_after_command}[/green]")
            print(
                f"{output.pyproject_toml_file_path} has {output.pyproject_toml_file_metadata_name} [green]{output.pyproject_toml_file_metadata_value_after_command}[/green]")
        else:
            print(
                f"{output.cff_file_path} has {output.common_metadata_name} [green]{output.cff_file_metadata_value_after_command}[/green]")
            print(
                f"{output.pyproject_toml_file_path} has {output.common_metadata_name} [green]{output.pyproject_toml_file_metadata_value_after_command}[/green]")
    else:
        print_json(output.model_dump_json())


@app_view.command("version")
def view_version(
        ctx: typer.Context,
        cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View version information for CITATION.CFF and pyproject.toml
    """
    _view_metadata(ctx=ctx, common_metadata_name="version",
                   cff_file_path=cff_file_path,
                   pyproject_toml_file_path=pyproject_toml_path)


@app_view.command("license")
def view_license(
        ctx: typer.Context,
        cff_file_path: Annotated[str, typer.Option(help="CITATION.cff file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View license information for CITATION.CFF and pyproject.toml
    """
    _view_metadata(ctx=ctx, common_metadata_name="license",
                   cff_file_path=cff_file_path,
                   pyproject_toml_file_path=pyproject_toml_path)


@ app_view.command("title")
def view_title(
        ctx: typer.Context,
        cff_file_path: Annotated[str, typer.Option(help="CITATION.cff file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View title information for CITATION.CFF and pyproject.toml
    """
    _view_metadata(ctx=ctx, common_metadata_name="title",
                   cff_file_path=cff_file_path,
                   pyproject_toml_file_path=pyproject_toml_path)


@ app_view.command("repo")
def view_code_repository_url(
        ctx: typer.Context,
        cff_file_path: Annotated[str, typer.Option(help="CITATION.cff file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View code repository url information for CITATION.CFF and pyproject.toml
    """
    _view_metadata(ctx=ctx, common_metadata_name="code_repository_url",
                   cff_file_path=cff_file_path,
                   pyproject_toml_file_path=pyproject_toml_path)


@ app_view.command("description")
def view_description(
        ctx: typer.Context,
        cff_file_path: Annotated[str, typer.Option(help="CITATION.cff file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View description information for CITATION.CFF and pyproject.toml
    """

    _view_metadata(ctx=ctx, common_metadata_name="description",
                   cff_file_path=cff_file_path,
                   pyproject_toml_file_path=pyproject_toml_path)
