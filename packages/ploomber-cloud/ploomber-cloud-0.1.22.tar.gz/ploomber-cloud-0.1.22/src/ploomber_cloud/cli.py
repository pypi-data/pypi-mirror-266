import click

from ploomber_cloud import (
    api_key,
    deploy as deploy_,
    github as github_,
    init as init_,
    examples as examples_,
    delete as delete_,
    __version__,
)


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
@click.argument("key", type=str, required=True)
def key(key):
    """Set your API key"""
    api_key.set_api_key(key)


@cli.command()
@click.option(
    "--watch", is_flag=True, help="Track deployment status in the command line"
)
def deploy(watch):
    """Deploy your project to Ploomber Cloud"""
    deploy_.deploy(watch)


@cli.command()
@click.option(
    "--from-existing",
    "from_existing",
    is_flag=True,
    help="Choose an existing project to initialize from",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=None,
    help="Force initialize a project to override the config file",
)
def init(from_existing, force):
    """Initialize a Ploomber Cloud project"""
    init_.init(from_existing, force)


@cli.command()
def github():
    """Configure workflow file for triggering
    GitHub actions"""
    github_.github()


@cli.command()
@click.argument("name", type=str, required=False)
def examples(name):
    """Download an example from the doc repository"""
    examples_.examples(name)


@cli.command()
def delete():
    """Download an example from the doc repository"""
    delete_.delete()


if __name__ == "__main__":
    cli()
