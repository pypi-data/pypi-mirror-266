import typer
from typing_extensions import Annotated

from cff2toml.models.files.cff_file import DEFAULT_CITATION_CFF_FILE_PATH, CffFile
from cff2toml.models.files.pyproject_toml_file import DEFAULT_PYPROJECT_TOML_FILE_PATH, PyprojectTomlFile
from cff2toml.models.files.synchronizers.cff_and_pyproject_toml_file_synchronizer import CffAndPyprojectTomlFileSynchronizer

app_change = typer.Typer(no_args_is_help=True)


@app_change.command("version")
def change_version(version: Annotated[str, typer.Argument()],
                   cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                              )] = DEFAULT_CITATION_CFF_FILE_PATH,
                   pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
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
                   cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                              )] = DEFAULT_CITATION_CFF_FILE_PATH,
                   pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
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


@app_change.command("title")
def change_title(title: Annotated[str, typer.Argument()],
                 cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                            )] = DEFAULT_CITATION_CFF_FILE_PATH,
                 pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    Change both CITATION.CFF and pyproject.toml
    to have the same title.
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    file_sync = CffAndPyprojectTomlFileSynchronizer(
        cff_file=cff_file, pyproject_toml_file=pyproject_toml_file)
    file_sync.set_title(title=title)
    file_sync.save()
    print(f"[yellow]changing title metadata...[/yellow]")
    print(
        f"[green]changed title for[/green] {cff_file.file_path} to [green]{title}[/green]")
    print(
        f"[green]changed title for [/green] {pyproject_toml_file.file_path} to [green]{title}[/green]")


@app_change.command("description")
def change_description(description: Annotated[str, typer.Argument()],
                       cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                                  )] = DEFAULT_CITATION_CFF_FILE_PATH,
                       pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    Change both CITATION.CFF and pyproject.toml
    to have the same description.
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    file_sync = CffAndPyprojectTomlFileSynchronizer(
        cff_file=cff_file, pyproject_toml_file=pyproject_toml_file)
    file_sync.set_description(description=description)
    file_sync.save()
    print(f"[yellow]changing description metadata...[/yellow]")
    print(
        f"[green]changed description for[/green] {cff_file.file_path} to [green]{description}[/green]")
    print(
        f"[green]changed description for [/green] {pyproject_toml_file.file_path} to [green]{description}[/green]")


@app_change.command("repo")
def change_code_repository_url(code_repository_url: Annotated[str, typer.Argument()],
                               cff_file_path: Annotated[str, typer.Option(help="CFF file path"
                                                                          )] = DEFAULT_CITATION_CFF_FILE_PATH,
                               pyproject_toml_path: Annotated[str, typer.Option(help="pyproject.toml file path")] = DEFAULT_PYPROJECT_TOML_FILE_PATH):
    """
    Change both CITATION.CFF and pyproject.toml
    to have the same code repository url.
    """
    cff_file = CffFile(file_path=cff_file_path)
    pyproject_toml_file = PyprojectTomlFile(file_path=pyproject_toml_path)

    file_sync = CffAndPyprojectTomlFileSynchronizer(
        cff_file=cff_file, pyproject_toml_file=pyproject_toml_file)
    file_sync.set_code_repository_url(
        code_repository_url=code_repository_url)
    file_sync.save()
    print(f"[yellow]changing code_repository_url metadata...[/yellow]")
    print(
        f"[green]changed code_repository_url for[/green] {cff_file.file_path} to [green]{code_repository_url}[/green]")
    print(
        f"[green]changed code_repository_url for [/green] {pyproject_toml_file.file_path} to [green]{code_repository_url}[/green]")
