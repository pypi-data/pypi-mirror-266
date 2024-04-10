from pathlib import Path
from pyrecipes import COOKBOOK_DIR
from pyrecipes.chapter import Chapter
from pyrecipes.errors import ChapterNotFoundError


class CookBook:
    def __init__(self, cookbook_dir: Path = COOKBOOK_DIR) -> None:
        self.cookbook_dir = cookbook_dir
        self.chapters: dict[int, Chapter] = {}
        self._collect()

    def _collect(self):
        """Collects all chapters in cookbok_dir"""
        for chapter_dir in sorted(self.cookbook_dir.glob("[0-9]*")):
            chapter = Chapter(chapter_dir)
            self.chapters[chapter.number] = chapter

    @property
    def size(self):
        return sum(chapter.size for chapter in self)

    def search(self, pattern: str, ignore_case: bool = False):
        results = {}
        for chapter in self.chapters.values():
            matches = chapter.search(pattern, ignore_case)
            if matches:
                results.setdefault(chapter, {}).update(matches)
        return results

    def __getitem__(self, key):
        chapter = self.chapters.get(key)
        if chapter:
            return self.chapters.get(key)
        raise ChapterNotFoundError(key)

    def __iter__(self):
        for chapter in self.chapters.values():
            yield chapter


cookbook = CookBook(COOKBOOK_DIR)
