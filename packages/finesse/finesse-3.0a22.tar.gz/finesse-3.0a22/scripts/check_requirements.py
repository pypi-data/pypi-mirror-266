#!/usr/bin/env python

from __future__ import annotations

try:
    import tomllib

    # tomllib not available in python < 3.11
except ImportError:
    try:
        import tomli as tomllib
    except ImportError as e:
        raise ImportError("This pre-commit hook requires tomli on python < 3.11") from e

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).absolute().parent.parent
PYPROJECT_TOML = ROOT / "pyproject.toml"
ENVIRONMENT_YML = ROOT / "environment.yml"
ENVIRONMENT_WIN_YML = ROOT / "environment-win.yml"


class VersionMismatchError(ValueError):
    "Package mentioned twice with different versions"


class BuildReqMismatchError(ValueError):
    "Build requirements and 'inplacebuild' requirements not identical"


class CondaYamlMismatchError(ValueError):
    "Python requirements differ between posix and windows conda environment file"


class PyprojectCondaMismatchError(ValueError):
    """Python requirements not identical between pyproject.toml and conda environment
    files."""


class MissingSystemDependencyError(ValueError):
    """Conda environment file contains a system dependency not present in the hardcoded
    list."""


def parse_req_line(line: str) -> tuple[str, str]:
    """Parse a requirement spec into package name and requirement.

    "numpy > 1" -> ("numpy", ">1")

    Parameters
    ----------
    line : str
        Line from a requirement file, e.g. "numpy > 1"

    Returns
    -------
    tuple[str, str]
        Name, Requirement
    """
    line = re.sub(r"\s", repl="", string=line)
    # see https://peps.python.org/pep-0508/#names
    match = re.match(
        r"""(^
            [A-Z0-9] # start with at least 1 alpha-numerical character
            [A-Z0-9._-]* # any number of alphanumericals, dots, underscores or hyphens
            [A-Z0-9] # Final character can not be a dot, underscore or hyphen
            )
            (.*) # followed by possible requirements specifier
            """,
        line,
        flags=re.I | re.VERBOSE,
    )
    assert match is not None
    name = match.groups()[0].lower()
    if match.groups()[1]:
        req = match.groups()[1].lower()
    else:
        req = ""
    return name, req


def check_version_mismatch(deps: list[str], source: Path) -> None:
    versions = {}
    for dep in deps:
        name, req = parse_req_line(dep)
        if name in versions and versions[name] != req:
            raise VersionMismatchError(
                f"Dependency {name} specified twice with different versions in {source}"
                f"\n Version 1: '{req}'"
                f"\n Version 2: '{versions[name]}'"
            )
        else:
            versions[name] = req


def check_pyproject_toml() -> set[str]:
    """Checks whether the build requirements in the pyproject.toml are identical to the
    'inplacebuild' optional dependencies, and whether there are any packages listed
    twice with a different version requirement.

    Returns
    -------
    set[str]
        Set of all python requirements in the pyproject.toml file

    Raises
    ------
    ValueError
        When there is a mismatch between build requirements and 'inplacebuild'
        requirements
    """
    with open(PYPROJECT_TOML, "rb") as f:
        cfg = tomllib.load(f)
    build_system = set(cfg["build-system"]["requires"])
    inplacebuild = set(cfg["project"]["optional-dependencies"]["inplacebuild"])
    mismatch = build_system.symmetric_difference(inplacebuild)
    if mismatch:
        raise BuildReqMismatchError(
            f"Mismatch between build system requirements in pyproject.toml "
            f"and 'inplacebuild' optional requirements, "
            f" symmetric difference: {mismatch}"
        )
    optional_deps = sum(cfg["project"]["optional-dependencies"].values(), start=[])
    all_deps = cfg["project"]["dependencies"] + optional_deps
    check_version_mismatch(all_deps, PYPROJECT_TOML)
    return set(all_deps)


def check_environment_yaml_files() -> set[str]:
    """Checks whether the python dependencies in the posix and windows conda environment
    yml files are identical (excluding system dependencies), and whether they contain
    any duplicate entries with different versions.

    Returns
    -------
    set[str]
        Set of python requirements specified in the environment file
    """
    posix_sys_deps = {
        "make",
        "c-compiler",
        "suitesparse",
        "pip",
    }
    windows_sys_deps = {
        "m2-base",
        "m2w64-make",
        "suitesparse",
        "libpython",
        "pip",
    }
    with open(ENVIRONMENT_YML) as f:
        env_posix = yaml.load(f.read(), yaml.Loader)
    with open(ENVIRONMENT_WIN_YML) as f:
        env_windows = yaml.load(f.read(), yaml.Loader)
    # pip dictionary is last item in deps list
    posix_deps = env_posix["dependencies"].pop()["pip"] + env_posix["dependencies"]
    windows_deps = (
        env_windows["dependencies"].pop()["pip"] + env_windows["dependencies"]
    )
    check_version_mismatch(posix_deps, ENVIRONMENT_YML)
    check_version_mismatch(windows_deps, ENVIRONMENT_WIN_YML)
    posix_deps = set(posix_deps)
    windows_deps = set(windows_deps)
    # I think this only checks if items from the hardcoded list is missing?
    if posix_sys_deps - posix_deps != set():
        raise MissingSystemDependencyError(
            f"Unknown System dependency in {ENVIRONMENT_YML}\n"
            f"{posix_sys_deps - posix_deps}\n"
            f"Please update {check_environment_yaml_files.__name__} in {__file__}"
        )
    if windows_sys_deps - windows_deps != set():
        raise MissingSystemDependencyError(
            f"Unknown System dependency in {ENVIRONMENT_YML}\n"
            f"{windows_sys_deps - windows_deps}\n"
            f"Please update {check_environment_yaml_files.__name__} in {__file__}"
        )
    posix_python = posix_deps - posix_sys_deps
    windows_python = windows_deps - windows_sys_deps
    if posix_python != windows_python:
        mismatch = posix_python.symmetric_difference(windows_python)
        raise CondaYamlMismatchError(mismatch)
    return posix_python


def main():
    yaml_deps = check_environment_yaml_files()
    toml_deps = check_pyproject_toml()
    mismatch = yaml_deps.symmetric_difference(toml_deps)
    if mismatch:
        raise PyprojectCondaMismatchError(
            f"Mismatch between pyproject.toml dependencies and environment.yml "
            f"dependencies. \nSymmetric difference: {mismatch}"
        )


if __name__ == "__main__":
    main()
