import typer
from typing_extensions import Annotated

from cff2toml.models.files.cff_file import DEFAULT_CITATION_CFF_FILE_PATH, CffFile
from cff2toml.models.files.pyproject_toml_file import DEFAULT_PYPROJECT_TOML_FILE_PATH, PyprojectTomlFile
from cff2toml.models.files.synchronizers.cff_and_pyproject_toml_file_synchronizer import CffAndPyprojectTomlFileSynchronizer

app_view = typer.Typer(no_args_is_help=True)


@app_view.command("version")
def view_version(
        cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View version information for CITATION.CFF and pyproject.toml
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    print(f"[yellow]viewing version metadata...[/yellow]")
    print(
        f"{cff_file.file_path} has version [green]{cff_file.metadata_version}[/green]")
    print(
        f"{pyproject_toml_file.file_path} has version [green]{pyproject_toml_file.metadata_project_version}[/green]")


@app_view.command("license")
def view_license(
        cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View license information for CITATION.CFF and pyproject.toml
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    print(f"[yellow]viewing license metadata...[/yellow]")
    print(
        f"{cff_file.file_path} has license [green]{cff_file.metadata_license}[/green]")
    print(
        f"{pyproject_toml_file.file_path} has license [green]{pyproject_toml_file.metadata_project_license}[/green]")


@app_view.command("title")
def view_title(
        cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View title information for CITATION.CFF and pyproject.toml
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    print(f"[yellow]viewing title metadata...[/yellow]")
    print(
        f"{cff_file.file_path} has title [green]{cff_file.metadata_title}[/green]")
    print(
        f"{pyproject_toml_file.file_path} has title [green]{pyproject_toml_file.metadata_project_name}[/green]")


@app_view.command("repo")
def view_code_repository_url(
        cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View code repository url information for CITATION.CFF and pyproject.toml
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    print(f"[yellow]viewing code_repository_url metadata...[/yellow]")
    print(
        f"{cff_file.file_path} has code repository url [green]{cff_file.metadata_repository_code}[/green]")
    print(
        f"{pyproject_toml_file.file_path} has code repository url [green]{pyproject_toml_file.metadata_project_urls_source}[/green]")


@app_view.command("description")
def view_description(
        cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    View description information for CITATION.CFF and pyproject.toml
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    print(f"[yellow]viewing description metadata...[/yellow]")
    print(
        f"{cff_file.file_path} has description [green]{cff_file.metadata_abstract}[/green]")
    print(
        f"{pyproject_toml_file.file_path} has description [green]{pyproject_toml_file.metadata_project_description}[/green]")
