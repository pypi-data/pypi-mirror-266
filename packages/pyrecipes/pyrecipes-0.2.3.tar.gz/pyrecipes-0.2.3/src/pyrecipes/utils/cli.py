import re
import textwrap
from typing import Mapping
import click
from colorama import Fore
from colorama.ansi import AnsiFore
from pyrecipes.chapter import Chapter
from pyrecipes.recipe import Recipe, SearchMatch
from .text import text_border


def render_recipe(recipe: Recipe, describe: bool = False):
    click.echo(recipe)
    if describe:
        click.echo(
            Fore.YELLOW
            + textwrap.fill(
                recipe.get_docstring(),
                70,
                initial_indent="   ",
                subsequent_indent="   ",
            )
            + Fore.RESET
            + "\n"
        )


def render_chapter(chapter: Chapter, describe: bool = False):
    click.echo(text_border(str(chapter), side_symbol=" "))
    for recipe in chapter:
        render_recipe(recipe, describe)
    click.echo("")


def get_n_matches(matches):
    count = 0
    for recipes in matches.values():
        for matches in recipes.values():
            count += sum(match.count for match in matches)
    return count


def render_match(
    pattern: str, match: SearchMatch, color: AnsiFore, ignore_case: bool = False
):
    flags = re.IGNORECASE if ignore_case else 0
    text = re.sub(
        pattern,
        lambda match: f"{color}{match.group()}{Fore.RESET}",
        match.line_text,
        flags=flags,
    ).strip()
    click.echo(f"  Line {match.line_number}: {text}")


def render_matches(
    pattern: str,
    match_dict: Mapping[Chapter, Mapping],
    color: AnsiFore,
    ignore_case: bool = False,
    describe: bool = False,
):
    for chapter, recipes in match_dict.items():
        click.echo(text_border(str(chapter)))
        for recipe, matches in recipes.items():
            render_recipe(recipe, describe)
            for match in matches:
                render_match(pattern, match, color, ignore_case)
            click.echo("")
