import os
import typer

from cff2toml.models.agents.authors.cff_entity_author import CffEntityAuthor
from cff2toml.models.agents.authors.cff_person_author import CffPersonAuthor
from cff2toml.models.files.cff_file import CffFile

app_about: typer.Typer = typer.Typer(no_args_is_help=True)


@app_about.command("about")
def about():
    """
    Get version and other information about cff2toml
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
