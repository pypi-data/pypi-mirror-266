import click
from pyrecipes.cookbook import cookbook


@click.command()
def chapters():
    """List chapters"""
    for chapter in cookbook:
        click.echo(chapter)
