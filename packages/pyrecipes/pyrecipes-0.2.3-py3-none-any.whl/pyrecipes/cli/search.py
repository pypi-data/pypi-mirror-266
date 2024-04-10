import sys
import click
from colorama import Fore, init
from pyrecipes.cookbook import cookbook
from pyrecipes.utils.cli import get_n_matches, render_matches

init(autoreset=True)

COLORS = {
    "black": Fore.BLACK,
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
    "none": Fore.RESET,
}


@click.command()
@click.argument("pattern", type=str)
@click.option(
    "--color",
    type=click.Choice(COLORS.keys(), case_sensitive=False),
    default="red",
    help="Change the color used to highlight matches. The default is red.",
)
@click.option(
    "-i",
    "--ignore-case",
    is_flag=True,
    default=False,
    help="Make the search case-insensitive",
)
@click.option(
    "-c", "--count-only", is_flag=True, help="Return the count of matches only."
)
@click.option(
    "-d",
    "--describe",
    is_flag=True,
    help="Shows descriptions of the recipes",
)
def search(pattern, color, ignore_case, count_only, describe):
    """Search the recipes for a pattern

    \b
    - RegEx patterns are supported.
    - Searches are case-sensitive by default. Use the `-i` flag to make searches case-insensitive.
    - Use the `-c` flag to display count of matches.

    """
    color = COLORS.get(color)
    match_dict = cookbook.search(pattern, ignore_case)

    click.echo(f"Found {get_n_matches(match_dict):,} matches")

    if count_only:
        sys.exit(0)

    if match_dict:
        render_matches(pattern, match_dict, color, ignore_case, describe)
