import click

from .auth import login_command
from .rag import rag_group
from .run import run_group
from .suite import suite_group


@click.group()
def cli():
    pass


cli.add_command(login_command)
cli.add_command(suite_group)
cli.add_command(run_group)
cli.add_command(rag_group)
