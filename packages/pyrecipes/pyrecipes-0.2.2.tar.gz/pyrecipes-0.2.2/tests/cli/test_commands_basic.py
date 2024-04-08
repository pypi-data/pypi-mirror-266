import sys
import pytest
import shlex
from pyrecipes.cli import main


def patch_argv(monkeypatch, command):
    args = shlex.split(command)
    monkeypatch.setattr(sys, "argv", args)
    return monkeypatch


def call_main(capsys):
    with pytest.raises(SystemExit) as exc:
        main()
    out, err = capsys.readouterr()
    return exc, out, err


@pytest.mark.parametrize("command", ["recipes", "recipes -h", "recipes --help"])
def test_no_command_prints_help(monkeypatch, capsys, command):
    monkeypatch = patch_argv(monkeypatch, command)
    exc, out, err = call_main(capsys)

    assert exc.value.code == 0
    assert "The CLI tool to find and display helpful Python recipes" in out
    assert "Usage: " in out
    assert err == ""


@pytest.mark.parametrize("command", ["recipes chapters", "recipes chapters -h"])
def test_chapter(monkeypatch, capsys, command):
    monkeypatch = patch_argv(monkeypatch, command)
    exc, _, err = call_main(capsys)

    assert exc.value.code == 0
    assert err == ""


@pytest.mark.parametrize(
    "command",
    ["recipes ls", "recipes ls 1", "recipes ls -d", "recipes ls -h", "recipes ls 1000"],
)
def test_ls(monkeypatch, capsys, command):
    monkeypatch = patch_argv(monkeypatch, command)
    exc, _, err = call_main(capsys)

    assert exc.value.code == 0
    assert err == ""


@pytest.mark.parametrize(
    "command", ["recipes show -h", "recipes show 1 3", "recipes show 1 1000"]
)
def test_show(monkeypatch, capsys, command):
    monkeypatch = patch_argv(monkeypatch, command)
    exc, _, err = call_main(capsys)

    assert exc.value.code == 0
    assert err == ""


@pytest.mark.parametrize(
    "command", ["recipes run 1 3", "recipes run -h", "recipes run 1 1000"]
)
def test_run(monkeypatch, capsys, command):
    monkeypatch = patch_argv(monkeypatch, command)
    exc, _, err = call_main(capsys)

    assert exc.value.code == 0
    assert err == ""


@pytest.mark.parametrize(
    "command",
    [
        "recipes search test",
        "recipes search -h",
        "recipes search foobar",
        "recipes search test -c",
        "recipes search -i test",
    ],
)
def test_search(monkeypatch, capsys, command):
    monkeypatch = patch_argv(monkeypatch, command)
    exc, _, err = call_main(capsys)

    assert exc.value.code == 0
    assert err == ""
