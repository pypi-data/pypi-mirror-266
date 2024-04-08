import typer
from typing_extensions import Annotated
import os
from rich import print

from cff2toml.models.agents.authors.cff_entity_author import CffEntityAuthor
from cff2toml.models.agents.authors.cff_person_author import CffPersonAuthor
from cff2toml.models.files.cff_file import CffFile, DEFAULT_CITATION_CFF_FILE_PATH
from cff2toml.models.files.pyproject_toml_file import PyprojectTomlFile, DEFAULT_PYPROJECT_TOML_FILE_PATH
from cff2toml.models.files.synchronizers.cff_and_pyproject_toml_file_synchronizer import CffAndPyprojectTomlFileSynchronizer


app = typer.Typer(no_args_is_help=True)

app_change = typer.Typer(no_args_is_help=True)
app.add_typer(app_change, name="change",
              help="Change metadata for both CITATION.cff and pyproject.toml files.")
app_view = typer.Typer(no_args_is_help=True)
app.add_typer(app_view, name="view",
              help="View metadata for both CITATION.cff and pyproject.toml files.")


@app.command()
def version():
    """
    Version information about cff2toml
    """
    current_dir: str = os.path.dirname(os.path.abspath(__file__))
    citation_cff_file_path: str = os.path.join(
        current_dir, '..', 'CITATION.cff')  # in distribution folder
    if not os.path.isfile(path=citation_cff_file_path):
        citation_cff_file_path = os.path.join(
            current_dir, '..', '..', '..', 'CITATION.cff')
        if not os.path.isfile(path=citation_cff_file_path):
            raise Exception('Cannot find the CITATION.cff file.')

    cff_file: CffFile = CffFile(
        file_path=citation_cff_file_path)
    print("")
    print(f"[bold green]{cff_file.metadata_title}[/bold green]")
    print(
        f"[yellow]version[/yellow]: {cff_file.metadata_version}")
    print(f"[yellow]description[/yellow]: {cff_file.metadata_abstract}")
    print(f"[yellow]license[/yellow]: {cff_file.metadata_license}")
    print(
        f"[yellow]repository url[/yellow]: [link={cff_file.metadata_repository_code}]{cff_file.metadata_repository_code}[/link]")
    print(f"[yellow]authors:[/yellow]")
    for author in cff_file.authors:
        print("")
        if isinstance(author, CffPersonAuthor):
            print(
                f"[green]{author.format_full_name()}[/green] {'[yellow]<[/yellow]' + author.email + '[yellow]>[/yellow]' if author.email else ''}")
        elif isinstance(author, CffEntityAuthor):
            print(
                f"[green]{author.name}[/green] {'[yellow]<[/yellow]' + author.email + '[yellow]>[/yellow]' if author.email else ''}")
    print("")


@app_change.command("version")
def change_version(version: Annotated[str, typer.Argument()],
                   cff_file_path: Annotated[str, typer.Option(
                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
                   pyproject_toml_path: Annotated[str, typer.Option()] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    Change both CITATION.CFF and pyproject.toml
    to have the same version.
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    file_sync = CffAndPyprojectTomlFileSynchronizer(
        cff_file=cff_file, pyproject_toml_file=pyproject_toml_file)
    file_sync.set_version(version=version)
    file_sync.save()
    print(f"[yellow]changing version metadata...[/yellow]")
    print(
        f"[green]changed version for[/green] {cff_file.file_path} to [green]{version}[/green]")
    print(
        f"[green]changed version for[/green] {pyproject_toml_file.file_path} to [green]{version}[/green]")


@app_change.command("license")
def change_license(license: Annotated[str, typer.Argument()],
                   cff_file_path: Annotated[str, typer.Option(
                   )] = DEFAULT_CITATION_CFF_FILE_PATH,
                   pyproject_toml_path: Annotated[str, typer.Option()] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    Change both CITATION.CFF and pyproject.toml
    to have the same license.
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    file_sync = CffAndPyprojectTomlFileSynchronizer(
        cff_file=cff_file, pyproject_toml_file=pyproject_toml_file)
    file_sync.set_license(license=license)
    file_sync.save()
    print(f"[yellow]changing license metadata...[/yellow]")
    print(
        f"[green]changed license for[/green] {cff_file.file_path} to [green]{license}[/green]")
    print(
        f"[green]changed license for [/green] {pyproject_toml_file.file_path} to [green]{license}[/green]")


@app_view.command("version")
def view_version(
        cff_file_path: Annotated[str, typer.Option(
        )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option()] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
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
        cff_file_path: Annotated[str, typer.Option(
        )] = DEFAULT_CITATION_CFF_FILE_PATH,
        pyproject_toml_path: Annotated[str, typer.Option()] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
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
