import pytest
from pathlib import Path
from pyrecipes.recipe import Recipe, SearchMatch


def test_recipe__valid__exists(valid_recipe):
    assert valid_recipe.module == "example"
    assert valid_recipe.chapter == 1
    assert valid_recipe.chapter_name == "01_test_chapter"
    assert valid_recipe.number == 1
    assert valid_recipe.name == "01_test_recipe"
    assert valid_recipe.package == "pyrecipes.recipes0"
    assert valid_recipe.clean_name == "1) Test recipe"
    assert str(valid_recipe) == "1.1) Test recipe"
    assert valid_recipe.exists()


def test_recipe__valid__doesnt_exist(capsys):
    recipe = Recipe(Path("./01_testing_chapter/02_testing_example/"))
    recipe.run()
    out, err = capsys.readouterr()

    assert recipe.module == "example"
    assert recipe.chapter == 1
    assert recipe.chapter_name == "01_testing_chapter"
    assert recipe.number == 2
    assert recipe.name == "02_testing_example"
    assert recipe.package is None
    assert not recipe.exists()
    assert "Couldn't find Recipe" in out
    assert err == ""
    assert recipe.__repr__() == "Recipe(chapter=1, number=2)"
    with pytest.raises(ModuleNotFoundError, match="This recipe couldn't be found:"):
        recipe.get_module()


def test_recipes_running(recipe_path, capsys):
    recipe = Recipe(recipe_path)
    recipe.run()

    out, err = capsys.readouterr()
    assert "TODO" not in recipe.get_docstring()
    assert 'if __name__ == "__main__":' in recipe.get_code()
    assert f"Running {recipe.chapter}.{recipe.number}" in out
    assert err == ""


def test_recipes_search_found(valid_recipe):
    assert valid_recipe.search("TODO") == [
        SearchMatch(
            line_number=2,
            line_text="TODO\n",
            chapter=1,
            recipe_number=1,
            recipe_name="1) Test recipe",
            count=1,
        )
    ]


def test_recipes_search_ignore_case(valid_recipe):
    assert valid_recipe.search("todo", ignore_case=True) == [
        SearchMatch(
            line_number=2,
            line_text="TODO\n",
            chapter=1,
            recipe_number=1,
            recipe_name="1) Test recipe",
            count=1,
        )
    ]


def test_recipes_search__not_found(valid_recipe):
    assert valid_recipe.search("test") == []


def test_SearchMatches():
    matches = SearchMatch(1, "test", 2, 3, "test recipe", 1)
    assert matches.line_number == 1
    assert matches.line_text == "test"
    assert matches.chapter == 2
    assert matches.recipe_number == 3
    assert matches.recipe_name == "test recipe"
    assert matches.count == 1
    assert matches.__repr__() == (
        "SearchMatch(chapter=2, number=3, line_number=1, count=1)"
    )
