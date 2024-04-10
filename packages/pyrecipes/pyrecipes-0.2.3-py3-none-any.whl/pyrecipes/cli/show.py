import click
from pyrecipes.cookbook import cookbook
from pyrecipes.errors import ChapterNotFoundError, RecipeNotFoundError


@click.command()
@click.argument("chapter", type=int)
@click.argument("number", type=int)
def show(chapter, number):
    """Shows a recipe"""
    try:
        click.echo(f"Showing recipe {chapter}.{number}")
        click.echo(cookbook[chapter][number].get_code())
    except (ChapterNotFoundError, RecipeNotFoundError) as exc:
        click.echo(exc)
