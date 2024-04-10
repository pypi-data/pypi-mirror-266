from pathlib import Path
from .errors import RecipeNotFoundError
from .recipe import Recipe
from .utils.text import clean_text, extract_leading_numbers


class Chapter:
    def __init__(self, chapter_dir: Path):
        self.chapter_dir = chapter_dir
        self.recipes: dict[int, Recipe] = {}
        self._collect()

    @property
    def number(self):
        return extract_leading_numbers(self.chapter_dir.stem)

    @property
    def name(self):
        return self.chapter_dir.stem

    @property
    def size(self):
        return len(self.recipes)

    def search(self, pattern: str, ignore_case: bool = False):
        results = {}
        for recipe in self.recipes.values():
            matches = recipe.search(pattern, ignore_case)
            if matches:
                results.setdefault(recipe, []).extend(matches)
        return results

    def _collect(self):
        """Collects recipes"""
        for recipe_dir in sorted(self.chapter_dir.glob("[0-9]*")):
            recipe = Recipe(recipe_dir)
            self.recipes[recipe.number] = recipe

    def __getitem__(self, key):
        recipe = self.recipes.get(key)
        if recipe:
            return recipe
        raise RecipeNotFoundError(f"{self.number}.{key}")

    def __iter__(self):
        for recipe in self.recipes.values():
            yield recipe

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(number={self.number}, name={self.name}, recipes={len(self.recipes)})"

    def __str__(self) -> str:
        return f"{clean_text(self.name).title()}"
