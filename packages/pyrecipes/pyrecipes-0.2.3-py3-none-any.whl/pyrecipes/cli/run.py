import click
from pyrecipes.cookbook import cookbook
from pyrecipes.errors import ChapterNotFoundError, RecipeNotFoundError


@click.command()
@click.argument("chapter", type=int)
@click.argument("number", type=int)
def run(chapter, number):
    """Runs a recipe"""
    try:
        cookbook[chapter][number].run()
    except (ChapterNotFoundError, RecipeNotFoundError) as exc:
        click.echo(exc)
