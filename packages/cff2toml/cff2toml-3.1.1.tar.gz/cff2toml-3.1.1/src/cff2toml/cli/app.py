import typer
from cff2toml.cli.about_command.about_command import app_about
from cff2toml.cli.change_command.change_command import app_change
from cff2toml.cli.view_command.view_command import app_view

app = typer.Typer(no_args_is_help=True)

app.add_typer(app_about, name="about",
              help="View information about cff2toml.")


app.add_typer(app_change, name="change",
              help="Change metadata for both CITATION.cff and pyproject.toml files.")

app.add_typer(app_view, name="view",
              help="View metadata for both CITATION.cff and pyproject.toml files.")
