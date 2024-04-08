from dataclasses import dataclass
from pathlib import Path
from importlib import import_module
import re
from .utils.text import clean_text, extract_leading_numbers


@dataclass
class SearchMatch:
    line_number: int
    line_text: str
    chapter: int
    recipe_number: int
    recipe_name: str
    count: int

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"chapter={self.chapter}, "
            f"number={self.recipe_number}, "
            f"line_number={self.line_number}, "
            f"count={self.count})"
        )


class Recipe:
    module = "example"

    def __init__(self, recipe_dir: Path):
        self.recipe_dir = recipe_dir
        self.path = recipe_dir / f"{self.module}.py"

    @property
    def package(self):
        if self.exists():
            return f"pyrecipes.{self.path.parent.parent.parent.stem}"

    @property
    def chapter_name(self):
        return self.recipe_dir.parent.stem

    @property
    def name(self):
        return self.recipe_dir.stem

    @property
    def clean_name(self):
        return clean_text(self.name)

    @property
    def number(self):
        return extract_leading_numbers(self.name)

    @property
    def chapter(self):
        return extract_leading_numbers(self.chapter_name)

    def exists(self):
        return self.path.exists()

    def get_module(self):
        if not self.exists():
            raise ModuleNotFoundError(f"This recipe couldn't be found:\n  {self.path}")
        return import_module(
            f"{self.package}.{self.chapter_name}.{self.name}.{self.module}"
        )

    def get_docstring(self):
        return self.get_module().__doc__.strip()

    def get_code(self):
        return self.path.read_text()

    def run(self):
        if self.exists():
            print(f"Running {self.chapter}.{self.number} \n")
            getattr(self.get_module(), "main")()
            print()
        else:
            print(f"Couldn't find Recipe {self.name}")

    def search(self, pattern, ignore_case: bool = False):
        results = []
        flags = re.IGNORECASE if ignore_case else 0

        with self.path.open() as file:
            for i, line in enumerate(file, start=1):
                matches = re.findall(re.compile(pattern, flags=flags), line)
                if matches:
                    results.append(
                        SearchMatch(
                            line_number=i,
                            line_text=line,
                            chapter=self.chapter,
                            recipe_number=self.number,
                            recipe_name=self.clean_name,
                            count=len(matches),
                        )
                    )
        return results

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(chapter={self.chapter}, number={self.number})"
        )

    def __str__(self) -> str:
        return f"{self.chapter}.{self.clean_name}"
