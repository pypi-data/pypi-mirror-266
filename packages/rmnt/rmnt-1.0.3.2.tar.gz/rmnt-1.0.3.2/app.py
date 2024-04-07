import click
from rmnt.orchestrator import start

@click.group()
@click.version_option(version='1.0.0')
def cli():
    pass

@cli.command(help = "Create a New Project")
@click.argument("project_name")
def make(project_name):
    start(project_name)
    click.echo("Project Created Successfully!!")

if __name__=="__main__":
    cli()
