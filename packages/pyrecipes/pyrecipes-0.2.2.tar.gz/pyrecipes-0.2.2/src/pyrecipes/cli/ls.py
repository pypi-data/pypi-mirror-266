import click
from pyrecipes.cookbook import cookbook
from pyrecipes.errors import ChapterNotFoundError
from pyrecipes.utils.cli import render_chapter


@click.command()
@click.option(
    "-d",
    "--describe",
    is_flag=True,
    help="Shows descriptions of the recipes",
)
@click.argument("chapter", required=False, default=None, type=int)
def ls(chapter, describe):
    """List recipes

    \b
    The default behaviour lists the titles of all recipes for all chapters.
    Limit the output to a specific recipe by adding an additional 'CHAPTER'
    argument e.g. to list chapter 1 recipes

    \b
        recipes ls 1

    You can also add a '-d' flag to display a short description of each recipe.
    """
    if chapter:
        try:
            click.echo(f"{cookbook[chapter].size:,} recipes")
            render_chapter(cookbook[chapter], describe)
        except ChapterNotFoundError as exc:
            click.echo(exc)
    else:
        click.echo(f"{cookbook.size:,} recipes")
        for chapter in cookbook:
            render_chapter(chapter, describe)
