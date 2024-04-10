import pytest
from pyrecipes.chapter import Chapter
from pyrecipes.cookbook import CookBook
from pyrecipes.errors import ChapterNotFoundError


@pytest.fixture
def cookbook(recipe_root_dir):
    yield CookBook(recipe_root_dir)


def test_CookBook_init(cookbook, recipe_root_dir):
    assert cookbook.cookbook_dir == recipe_root_dir
    assert cookbook.chapters.keys() == {1, 2, 3}
    assert cookbook.size == 9


def test_CookBook_indexing__exists(cookbook):
    assert isinstance(cookbook[1], Chapter)


def test_CookBook_indexing__doesnt_exist(cookbook):
    with pytest.raises(ChapterNotFoundError, match="Chapter 100 not found"):
        _ = cookbook[100]


def test_iterating_over_CookBook(cookbook):
    for chapter, expected in zip(cookbook, [1, 2, 3]):
        assert chapter.number == expected
        assert isinstance(chapter, Chapter)
