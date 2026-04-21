import os
from types import SimpleNamespace


from alpha import cli


def test_main_dispatches_to_matching_handler(
    monkeypatch, fake_handler, sections
):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["alpha", "api", "gen", "--spec-file", "custom.yaml"],
    )

    cli.main(sections=sections)

    assert fake_handler.called is True
    assert fake_handler.kwargs == {"spec_file": "custom.yaml"}


def test_main_prints_section_help_when_command_missing(
    monkeypatch, capsys, fake_handler, sections
):
    monkeypatch.setattr(cli.sys, "argv", ["alpha", "api"])

    cli.main(sections=sections)

    output = capsys.readouterr().out
    assert "usage:" in output
    assert "gen" in output
    assert fake_handler.called is False


def test_main_prints_root_help_when_parse_result_lacks_command(
    monkeypatch, capsys, fake_handler, sections
):
    monkeypatch.setattr(cli.sys, "argv", ["alpha"])

    cli.main(sections=sections)

    output = capsys.readouterr().out
    assert "Alpha command line interface." in output
    assert "Use one of the sub categories" in output
    assert fake_handler.called is False


def test_main_prints_message_when_no_handler_matches(
    monkeypatch, capsys, fake_handler, sections
):
    def _fake_parse_args(_self):
        return SimpleNamespace(section="api", command="unknown")

    monkeypatch.setattr(
        cli.argparse.ArgumentParser, "parse_args", _fake_parse_args
    )

    cli.main(sections=sections)

    output = capsys.readouterr().out
    assert "No handler found, you should never read this" in output
    assert fake_handler.called is False


def test_guess_current_package_name_from_project_table(tmp_path, monkeypatch):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'my-service'\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = cli._guess_current_package_name()

    assert result == "my_service"


def test_guess_current_package_name_from_poetry_table(tmp_path, monkeypatch):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[tool.poetry]\nname = 'poetry-service'\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = cli._guess_current_package_name()

    assert result == "poetry_service"


def test_guess_current_package_name_finds_pyproject_in_subfolder(
    tmp_path, monkeypatch
):
    subproject = tmp_path / "service"
    subproject.mkdir()
    (subproject / "pyproject.toml").write_text(
        "[project]\nname = 'sub-project'\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = cli._guess_current_package_name()

    assert result == "sub_project"


def test_guess_current_package_name_falls_back_to_folder_name(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)

    result = cli._guess_current_package_name()

    output = capsys.readouterr().out
    assert "Could not find pyproject.toml" in output
    assert "Guessing package name from folder" in output
    assert result == os.path.basename(tmp_path)


def test_init_sets_container_config_and_wires(monkeypatch, fake_container):
    main_called = {"value": False}

    monkeypatch.setattr(cli, "Container", lambda: fake_container)
    monkeypatch.setattr(
        cli, "_guess_current_package_name", lambda: "my_service"
    )

    def _fake_main() -> None:
        main_called["value"] = True

    monkeypatch.setattr(cli, "main", _fake_main)

    cli.init()

    assert fake_container.config.api_package_name.value == "my_service_api"
    assert fake_container.config.service_package_name.value == "my_service"
    assert (
        fake_container.config.container_import.value
        == "from my_service.containers.container import Container"
    )
    assert fake_container.config.init_container_from.value == "my_service"
    assert (
        fake_container.config.init_container_function.value == "init_container"
    )
    assert fake_container.wire_called_with == [cli.sys.modules[cli.__name__]]
    assert main_called["value"] is True


def test_init_still_wires_and_runs_main_when_guess_is_empty(
    monkeypatch, fake_container
):
    main_called = {"value": False}

    monkeypatch.setattr(cli, "Container", lambda: fake_container)
    monkeypatch.setattr(cli, "_guess_current_package_name", lambda: "")

    def _fake_main() -> None:
        main_called["value"] = True

    monkeypatch.setattr(cli, "main", _fake_main)

    cli.init()

    assert fake_container.config.api_package_name.value is None
    assert fake_container.config.service_package_name.value is None
    assert fake_container.config.container_import.value is None
    assert fake_container.config.init_container_from.value is None
    assert fake_container.config.init_container_function.value is None
    assert fake_container.wire_called_with == [cli.sys.modules[cli.__name__]]
    assert main_called["value"] is True
