from typing_extensions import Annotated
import typer
from cff2toml.cli.about_command.about_command import about_command
from cff2toml.cli.change_command.change_command import app_change
from cff2toml.cli.context_helpers import TyperContextDictionary
from cff2toml.cli.view_command.view_command import app_view

app = typer.Typer(no_args_is_help=True)


# if you ever want to add a parameter that works without having to invoke a command
# then you need to use the 'invoke_without_command=True' argument for the callback decorator
# https://typer.tiangolo.com/tutorial/commands/context/

@app.callback()
def main(ctx: typer.Context, quiet: Annotated[bool, typer.Option(help="Hidden output mode (Only for 'change' command)")] = False, verbose: Annotated[bool, typer.Option(help="Verbose output mode")] = False, json: Annotated[bool, typer.Option(help="JSON output mode")] = False):
    d = TyperContextDictionary(ctx=ctx)
    d.set('quiet', quiet)
    d.set('verbose', verbose)
    d.set('json', json)


@app.command(name="about", help="View information about cff2toml.")
def about(ctx: typer.Context):
    about_command(ctx=ctx)


app.add_typer(app_change, name="change",
              help="Change metadata to specific value for both CITATION.cff and pyproject.toml files.")

app.add_typer(app_view, name="view",
              help="View metadata for both CITATION.cff and pyproject.toml files.")
