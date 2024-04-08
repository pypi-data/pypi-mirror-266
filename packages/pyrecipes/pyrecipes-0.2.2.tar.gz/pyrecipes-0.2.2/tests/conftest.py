import pytest
from pyrecipes import COOKBOOK_DIR, TEMPLATE_PATH
import pyrecipes
from pyrecipes.recipe import Recipe


TEMPLATE = TEMPLATE_PATH.read_text()


@pytest.fixture(params=list(COOKBOOK_DIR.glob("**/example.py")))
def recipe_path(request):
    """Iters over every recipe."""
    yield request.param.parent


@pytest.fixture(scope="session")
def recipe_root_dir(tmp_path_factory):
    """Creates dummy recipe dir with chapters 1, 2, 3 each with 3 example recipes."""
    root_dir = tmp_path_factory.mktemp("recipes")
    (root_dir / "template.py").write_text(TEMPLATE)

    for i in range(1, 4):
        chapter_dir = root_dir / f"0{i}_test_chapter"
        for j in range(1, 4):
            recipe_dir = chapter_dir / f"0{j}_test_recipe"
            recipe_dir.mkdir(parents=True, exist_ok=True)
            (recipe_dir / "example.py").write_text(TEMPLATE)
    yield root_dir


@pytest.fixture
def valid_recipe(recipe_root_dir):
    yield Recipe(recipe_root_dir / "01_test_chapter" / "01_test_recipe")


@pytest.fixture
def patched_root(recipe_root_dir, monkeypatch):
    """Patches the real root recipe directory for the testing dummy one"""
    monkeypatch.setattr(pyrecipes, "ROOT", recipe_root_dir)
    yield monkeypatch
