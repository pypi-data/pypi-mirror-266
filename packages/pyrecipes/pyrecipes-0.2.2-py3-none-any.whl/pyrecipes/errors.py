from typing import Any


class ChapterNotFoundError(Exception):
    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"Chapter {value} not found")


class RecipeNotFoundError(Exception):
    def __init__(self, value: Any):
        self.value = value
        super().__init__(f"Recipe {value} not found")
