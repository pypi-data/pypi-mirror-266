from pathlib import Path

import pytest

from nens_meta import pyproject_toml


@pytest.fixture
def empty_python_config(tmp_path: Path) -> pyproject_toml.PyprojectToml:
    pyproject_toml.create_if_missing(tmp_path)
    return pyproject_toml.PyprojectToml(tmp_path, {})


def test_pyproject_toml_file(tmp_path: Path):
    assert pyproject_toml.pyproject_toml_file(tmp_path).name == "pyproject.toml"


def test_create_if_missing(tmp_path: Path):
    pyproject_toml.create_if_missing(tmp_path)
    assert (tmp_path / "pyproject.toml").exists()


def test_read(empty_python_config: pyproject_toml.PyprojectToml):
    assert empty_python_config._contents == {}


def test_get_or_create_section1(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config.get_or_create_section("reinout")
    empty_python_config.write()
    assert "[reinout]" in empty_python_config._config_file.read_text()


def test_get_or_create_section(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config.get_or_create_section("reinout.van")
    empty_python_config.write()
    assert "[reinout.van]" in empty_python_config._config_file.read_text()


def test_adjust_build_system(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config.adjust_build_system()
    empty_python_config.write()
    assert "setuptools>=" in empty_python_config._config_file.read_text()


def test_adjust_project(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config._options = {
        "project_name": "pietje",
    }
    empty_python_config.adjust_project()
    empty_python_config.write()
    assert "pietje" in empty_python_config._config_file.read_text()
    assert "dependencies" in empty_python_config._config_file.read_text()


def test_package_name1(empty_python_config: pyproject_toml.PyprojectToml):
    # Default case
    empty_python_config._options = {
        "package_name": "pietje_klaasje",
    }
    assert empty_python_config.package_name == "pietje_klaasje"


def test_package_name2(empty_python_config: pyproject_toml.PyprojectToml):
    # package_name not set, we get a default dummy one
    assert empty_python_config.package_name == "not_set"


def test_adjust_setuptools1(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config._options = {
        "project_name": "pietje-klaasje",
        "package_name": "pietje_klaasje",
    }
    empty_python_config.adjust_setuptools()
    empty_python_config.write()
    assert (
        'packages = ["pietje_klaasje"]' in empty_python_config._config_file.read_text()
    )


def test_ensure_setuptools2(empty_python_config: pyproject_toml.PyprojectToml):
    # Corner case: init file without version.
    package_dir = empty_python_config._project / "pietje_klaasje"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("# Empty")
    empty_python_config._options = {
        "project_name": "pietje-klaasje",
        "package_name": "pietje_klaasje",
    }
    empty_python_config.adjust_setuptools()
    # No assert needed.


def test_ensure_setuptools1pytest(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config._options = {
        "package_name": "pietje_klaasje",
    }
    empty_python_config.adjust_pytest()
    empty_python_config.write()
    assert "log_level" in empty_python_config._config_file.read_text()
    assert '["pietje_klaasje"]' in empty_python_config._config_file.read_text()


def test_ensure_coverage(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config._options = {
        "package_name": "pietje_klaasje",
    }
    empty_python_config.adjust_coverage()
    empty_python_config.write()
    assert "source" in empty_python_config._config_file.read_text()
    assert "pietje_klaasje" in empty_python_config._config_file.read_text()


def test_adjust_ruff(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config._options = {
        "package_name": "pietje_klaasje",
    }
    empty_python_config.adjust_ruff()
    empty_python_config.write()
    assert "[tool.ruff.lint]" in empty_python_config._config_file.read_text()
    assert "target-version" in empty_python_config._config_file.read_text()


def test_adjust_zestreleaser(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config.adjust_zestreleaser()
    empty_python_config.write()
    assert "release = false" in empty_python_config._config_file.read_text()


def test_ensure_pyright(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config._options = {
        "package_name": "pietje_klaasje",
    }
    empty_python_config.adjust_pyright()
    empty_python_config.write()
    assert "[tool.pyright]" in empty_python_config._config_file.read_text()
    assert "pietje_klaasje" in empty_python_config._config_file.read_text()


def test_remove_old_sections(empty_python_config: pyproject_toml.PyprojectToml):
    empty_python_config._config_file.write_text("[tool.isort]\nreinout = 1972")
    empty_python_config.read()
    empty_python_config.remove_old_sections()
    empty_python_config.write()
    assert "reinout" not in empty_python_config._config_file.read_text()


def test_move_outdated_files(empty_python_config: pyproject_toml.PyprojectToml):
    example = empty_python_config._project / ".flake8"
    example.write_text("")
    empty_python_config.move_outdated_files()
    assert not example.exists()
    new_example = empty_python_config._project / ".flake8.outdated"
    assert new_example.exists()


def test_move_outdated_files2(empty_python_config: pyproject_toml.PyprojectToml):
    # First zap existing '.outdated' files.
    example = empty_python_config._project / ".flake8"
    example.write_text("current")
    example2 = empty_python_config._project / ".flake8.outdated"
    example2.write_text("old")
    empty_python_config.move_outdated_files()
    assert not example.exists()
    assert example2.exists()
    assert "current" in example2.read_text()


def test_write_documentation():
    pyproject_toml.write_documentation()
