"""
dsvenv - a tool to manage Python virtual environments for DS projects.

dsvenv is created on top of several other Python tools (venv, pip, pre-commit) and
serves to simplify the setup of the projects for developers. On Windows, it allows
specifying the Python version (>3.5) that should be used for the virtual environment.

Ideally after cloning the new repository you would need to execute a single command:
  $ dsvenv
or
  $ python -m dsvenv

If the execution succeeds, a new `.venv` folder should appear in the current working
directory containing (besides Python and pip itself):

    * A pip configuration file (`.venv/pip.ini` or `.venv/pip.conf`) with any parameters
        provided in a project configuration file (typically `setup.cfg`);

    * Any additional packages specified in requirement files provided (by default,
        only `requirements.txt` will be picked up);

    * Pre-commit hooks installed as specified by the pre-commit configuration file
        (i.e., `.pre-commit-config.yaml`);

DS-specific:
    Additionally, if a file `azure-pipelines.yml` is present, the created environment
    is verified against the environment specification therein, and suitable warnings
    are printed if discrepancies are found.


dsvenv uses two important concepts that are similar but different:

    * venv - a virtual environment that was created from some Python executable using
        the `venv` module. As a result it is as isolated as `venv` allows, but doesn't
        allow creating further venvs from it. This is a working environment for the
        project.

    * base venv - a base virtual environment - on Windows it corresponds to a small
        isolated Python and pip installation. It is then used to create project venvs
        using `venv` and is completely independent from a system Python. There can
        be multiple base venvs on the same machine (one per Python version ever used).
        On other operating systems (Linux, macOS) this functionality is not implemented,
        so we are cheating by claiming that only a base venv of the same version as the
        system Python exist (this is done purely for convenience). The application will
        fail spectacularly if trying to ask for non-system Python on Linux.


This leads to the following universal procedure:

    1. Selection of the Python version
       A Python version can contain a '*' symbol and will be resolved according to the
       'Version matching' rule of PEP440. I.e. it is allowed to use 3.8, 3.8.5 or 3.8.*.
       For more information on PEP440 check the following URL:
       https://www.python.org/dev/peps/pep-0440/#version-matching
       A Python version can be specified in multiple places with the following priority:
       - command line parameter;
       - setup.cfg file (section 'dsvenv', option 'python_version');
       - existing virtual environment Python;
       - system python.

    2. If the project already contains a venv - `dsvenv` will only proceed if it is
       compatible with the requested Python version or if you explicitly request to
       remove it.

    3. If the project does NOT contain a venv - it will be created from a base venv.
       If a base venv of the requested version doesn't exist it will be created. If the
       base venv of the requested version does exist it will be used without the check
       for a possibly newer version. I.e. if you requested Python 3.8.* and you already
       have 3.8.1 - it will be used even if 3.8.9 is available for installation.

    4. Any required packages will be installed (possible custom pip configuration). Any
       packages can be specified via the requirement files (using `-r` option) or in the
       configuration file (`requires` option of `dsvenv` section). Additionally the
       latter option allows to specify '===None' as the package specification - this
       means that the package won't be installed even if dsvenv usually does it by
       default.
       The order of the package installation is the following:
       - `pip` and `setuptools` (installed with `--upgrade` flag);
       - `keyring` and `artifacts-keyring` - to ensure access to Azure Artifacts;
       - other packages for the build system specified in configuration file;
       - other packages specified in requirements files.

    5. The environment will be verified.

    6. Pre-commit hooks will be installed if `.pre-commit-config.yaml` can be found.
"""

import ast
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import traceback
import zipfile
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser, NoSectionError
from pathlib import Path
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Union
from urllib.request import urlopen

from packaging.requirements import Requirement
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import Version
from pip._internal.configuration import CONFIG_BASENAME as _PIP_CONF

try:
    import colorlog
except ImportError:
    pass


# Local Folder
from . import __version__


def path_or_none(path: Path) -> Optional[Path]:
    """
    A small helper that returns a `path` if it exists or `None` otherwise.
    """
    return path if path.exists() else None


_DEFAULT_SETUP_CFG = path_or_none(Path.cwd() / 'setup.cfg')
_DEFAULT_REQUIREMENTS_TXT = path_or_none(Path.cwd() / 'requirements.txt')
_DEFAULT_PRE_COMMIT_YAML = path_or_none(Path.cwd() / '.pre-commit-config.yaml')
_DEFAULT_AZURE_PIPELINES_YAML = path_or_none(Path.cwd() / 'azure-pipelines.yml')
_LEGACY_AZURE_PIPELINES_YAML = path_or_none(Path.cwd() / 'azure.yml')

# A base URL for the Nuget package service used to install Python into the base
# environment on Windows
_NUGET_PACKAGE_BASE_URL = 'https://api.nuget.org/v3-flatcontainer'

# Any requirements that MUST be present in the virtual environment and cannot be
# excluded using '===None' syntax
_MANDATORY_DSVENV_REQUIRES = ['pip', 'setuptools']

# The requirements that need to be installed in order to use the Azure Artifacts PyPi.
# They can be excluded, but pip won't be able to properly handle the custom Azure index
# without them.
_MANDATORY_AZURE_ARTIFACTS_REQUIRES = ['keyring', 'artifacts-keyring']


def _parse_requirements(requirements: List[str]) -> Dict[str, Requirement]:
    """
    Parse the requirements using setuptools and return a dictionary of them.

    Args:
        requirements: A list of pip requirements.

    Returns:
        A dictionary with the package names as keys and the full requirement specs as
            values.
    """
    return {Requirement(r).name: Requirement(r) for r in requirements}


# These are the default versions specifications of packages needed to be installed.
_DEFAULT_DSVENV_REQUIRES = _parse_requirements(
    [
        *_MANDATORY_DSVENV_REQUIRES,
        *_MANDATORY_AZURE_ARTIFACTS_REQUIRES,
        'dsbuild==0.0.8',
    ]
)

_THIS_PYTHON_VERSION = '{}.{}.{}'.format(*sys.version_info[:3])

_VENV_BIN_SEARCH_DIRS = ['.', 'Scripts', 'bin']

if sys.platform == 'win32':
    _BASE_ENVS_DIR = Path(
        os.environ.get(
            'DSVENV_BASE_ENVS_DIR',
            Path(os.environ['LOCALAPPDATA']) / 'dsvenv' / 'base_envs',
        )
    )


PipConfig = dict


class AzurePipelinesConfig(NamedTuple):
    python_version: Optional[str] = None
    dsvenv_version: Optional[str] = None


class DSVenvConfig(NamedTuple):
    python_version: str = _THIS_PYTHON_VERSION
    azure_pipelines_yml: Optional[Path] = (
        _DEFAULT_AZURE_PIPELINES_YAML or _LEGACY_AZURE_PIPELINES_YAML
    )
    requires: Dict[str, Requirement] = _DEFAULT_DSVENV_REQUIRES


def setup_logging(loglevel: int = logging.INFO):
    """
    Sets up the logger for the script.

    The logs will have a format: TIMESTAMP LEVEL: MESSAGE
    If `colorlog` is installed and running inside a tty the log messages will be
    colored.

    Args:
        logLevel: A level of log messages to display.
    """
    root = logging.getLogger()
    root.setLevel(loglevel)
    log_format = '%(asctime)s %(levelname)s: %(message)s'
    if 'colorlog' in sys.modules and os.isatty(2):
        colorlog_format = '%(log_color)s' + log_format
        formatter = colorlog.ColoredFormatter(colorlog_format)
    else:
        formatter = logging.Formatter(log_format)
    log_hangler = logging.StreamHandler()
    log_hangler.setFormatter(formatter)
    root.addHandler(log_hangler)


def check_call(executable: Path, *args: str, **kwargs: Dict[str, Any]):
    """
    Runs `subprocess.check_call` ensuring that all the arguments are strings.

    This is a convenience wrapper for `subprocessing.check_call`, which allows
    passing any values as the arguments (e.g. pathlib.Path) without the explicit
    conversion to `str`.

    All the non-keyword arguments (`executable` and `args`) will be passed to the
    `check_call` as a list. This means that any keyword arguments **must** use the
    keywords, otherwise they will be treated as the arguments for the executable.

    Args:
        executable: A path to the executable to call, e.g. echo.

        args: any arguments to use for calling the executable, e.g. 'hello', 'world'.

        kwargs: any keyword arguments to pass to `subprocess.check_call`, e.g. stdin,
            stdout and stderr.

    Raises:
        `CalledProcessError` if the return code of the command is not zero.
    """
    args_str = [str(a) for a in [executable, *args]]
    subprocess.check_call(args_str, **kwargs)  # type: ignore[arg-type]


def check_output(executable: Path, *args: str, **kwargs: Dict[str, Any]) -> str:
    """
    Runs `subprocess.check_output` ensuring that all the arguments are strings.

    This is a convenience wrapper for `subprocessing.check_output`, which allows
    passing any values as the arguments (e.g. pathlib.Path) without the explicit
    conversion to `str`.

    All the non-keyword arguments (`executable` and `args`) will be passed to the
    `check_call` as a list. This means that any keyword arguments **must** use the
    keywords, otherwise they will be treated as the arguments for the executable.

    Args:
        executable: A path to executable to call, e.g. 'echo'.

        args: any arguments to use for calling the executable,
            e.g. 'hello', 'world'.

        kwargs: any keyword arguments to pass to `subprocess.check_output`, e.g. stdin,
            stdout and stderr.

    Returns:
        A decoded output of the call.

    Raises:
        `CalledProcessError` if the return code of the command is not zero.
    """
    args_str = [str(a) for a in [executable, *args]]
    out = subprocess.check_output(args_str, **kwargs)  # type: ignore[call-overload]
    return out.decode()


def as_specifier(specifier: str) -> SpecifierSet:
    """
    Try to convert a version specifier to a `SpecifierSet`.

    Args:
        specifier: A version specifier to convert.

    Returns:
        A `SpecifierSet` object.

    Raises:
        InvalidSpecifier: if the version specification is not correct.
    """
    try:
        conv_specifier = SpecifierSet(specifier)
    except InvalidSpecifier:
        try:
            conv_specifier = SpecifierSet(f'=={specifier}')
        except InvalidSpecifier:
            raise InvalidSpecifier(
                f'The version specification {specifier} is incorrect. Supported '
                f'formats are e.g. 1.2.3, 1.2.*, >=1.2.3, ~=1.2.3, !=1.2.3, '
                f'<=1.2.3, >1.2.3, <1.2.3, >=1.2, <1.3, >=1.2, <1.3.'
            )
    return conv_specifier


def version_matches_spec(version_to_check: str, version_spec: str) -> bool:
    """
    Checks if a version string matches a given version specification.

    This function allows both 'version matching' and 'version specification' matching.
    For 'version matching', if the user provides a version number then '==' is added in
    front and matching is done according to PEP440 definition (which allows using
    trailing wildcards and zero-padding):
    https://www.python.org/dev/peps/pep-0440/#version-matching
    If user provide a version specification e.g. (~=1.2.3, ==1.2.3 or even
    '>= 1.0, < 2.0') then it is used as is. More examples can be found here:
    https://peps.python.org/pep-0440/#examples

    Args:
        version_to_check: A version that should be checked.

        version_spec: A version (e.g. 1.2.3, 1.2.*) or a version specification
            (>= 1.0).

    Returns:
        `True` if the versions matches the spec according to the following table:
        version     | spec  | Result
        ----------------------------
        1.2.3       | 1.2.3 | True
        1.2.3       | 1.2.* | True
        1.2.3       | 1.*   | True
        1.2.0       | 1.2   | True
        1.0.0       | 1     | True
        1.2         | 1.2.0 | True
        1           | 1.0.0 | True
        1.0.0       | 1     | True
        >1.2.2      | 1.2.3 | True
        ~=1.2.3     | 1.2.4 | True
        >=1.0, <2.0 | 1.2.3 | True
        1.2.3       | 1.2.9 | False
        1.2.10      | 1.2.1 | False
        1.2.3       | 1.2   | False
        1.2.3       | 1     | False
        >1.2.3      | 1.2.3 | False
        ~=1.2.3     | 1.3.3 | False
        >=1.0, <2.0 | 2.2.3 | False
    """
    version = Version(version_to_check)
    specifier = as_specifier(version_spec)
    return version in specifier


def python_version_matches_spec(version_to_check: str, version_spec: str) -> bool:
    """
    Checks if a Python version string matches a given version specification.

    For the moment it works in exactly the same way as a `version_matches_spec`,
    but this may change in future.

    Args:
        version_to_check: A version that should be checked.

        version_spec: A version specification (e.g. 1.2.3 or 1.2.*)

    Returns:
        `True` if the versions matches.
    """
    return version_matches_spec(version_to_check, version_spec)


def venv_exists(venv_dir: Path) -> bool:
    """
    Verifies if the virtual environment exists in the specified directory.

    Args:
        venv_dir: A path to check.

    Returns:
        `True` if the virtual environment exists and contains a Python executable.
    """
    return venv_dir.is_dir() and venv_python_exists(venv_dir)


def list_base_venv_python_versions() -> List[str]:
    """
    List all the base python versions in descending order.
    """
    if not _BASE_ENVS_DIR.is_dir():
        return []

    dirs = [d.name for d in _BASE_ENVS_DIR.iterdir() if venv_exists(d)]
    versions = sorted((Version(d) for d in dirs), reverse=True)
    return [f'{v}' for v in versions]


def list_available_to_download_python_versions() -> List[str]:
    """
    List all the Python versions available for downloading.

    Any of these versions can then be downloaded to create a local base Python
    environment.

    Returns:
        A list of Python versions in descending order.

    Raises:
        EnvironmentError: If running on non-Windows OS.
        RuntimeError: If for any reason cannot retrieve the list of versions online.
    """
    if sys.platform != 'win32':
        raise EnvironmentError(
            f'Custom Python version is not supported on your platform '
            f'({sys.platform}). You can only use system Python '
            f'{_THIS_PYTHON_VERSION}.'
        )

    try:
        versions_url = f'{_NUGET_PACKAGE_BASE_URL}/python/index.json'
        with urlopen(versions_url) as response:
            available_versions = json.loads(response.read())['versions']
            available_versions = sorted(
                (Version(v) for v in available_versions), reverse=True
            )
            return [f'{v}' for v in available_versions]
    except Exception as e:
        raise RuntimeError(
            f'Error retrieving a list of available Python versions from {versions_url}.'
            f'Exact error: {e}.'
        )


def clean_python_version_spec(python_version_spec: str) -> str:
    """
    Cleans up the Python version specification.

    The function removes trailing comments from the version specification as well as
    leading and trailing spaces and quotes.

    Args:
        python_version_spec: A Python version specification.

    Returns:
        A cleaned up version specification.
    """
    # Matches any spaces and quotes.
    sp_or_q = r'[\s\t]*[\'"]?[\s\t]*'
    # Remove trailing comments and any leading and trailing spaces and quotes.
    python_version_spec = re.sub(
        r'^' + sp_or_q + r'|' + sp_or_q + r'#.*$|' + sp_or_q + r'$',
        '',
        python_version_spec,
    )

    return python_version_spec


def resolve_python_version_spec(python_version_spec: str) -> str:
    """
    Resolves a Python version specification to a version that can be used for venv.

    On Windows it first considers the highest compatible version available already
    locally as a base venv. If nothing is suitable, it looks for a the highest
    compatible version online.

    On other platforms it will always return a version of the system Python if it is
    compatible with the version specification.

    Args:
        python_version_spec: A Python version specification.

    Returns:
        A Python version compatible with the given specification. As a result running
        `create_base_venv` should succeed if provided with this parameter.

    Raises:
        RuntimeError: If the compatible version cannot be found.
    """
    python_version_spec = clean_python_version_spec(python_version_spec)

    def get_compatible_version(versions, python_version_spec):
        return next(
            (
                v
                for v in versions
                if python_version_matches_spec(v, python_version_spec)
            ),
            None,
        )

    if sys.platform != 'win32':
        if python_version_matches_spec(_THIS_PYTHON_VERSION, python_version_spec):
            logging.info(
                f'Your system Python {_THIS_PYTHON_VERSION} is compatible with the '
                f'specification of {python_version_spec}. It will be used to create a '
                f'virtual environment. Specifying any other version works only in '
                f'Windows while you are working on {sys.platform} platform.'
            )
            return _THIS_PYTHON_VERSION
        else:
            raise RuntimeError(
                f'Custom Python version is not supported on your platform '
                f'({sys.platform}). You can only use system Python compatible with '
                f'{_THIS_PYTHON_VERSION}.'
            )

    compatible_version = get_compatible_version(
        list_base_venv_python_versions(), python_version_spec
    )
    if compatible_version is not None:
        logging.info(
            f'A base environment of Python {compatible_version} found which is '
            f'compatible with the specification of {python_version_spec}. it will '
            f'be used to create a virtual environment.'
        )
        return compatible_version

    compatible_version = get_compatible_version(
        list_available_to_download_python_versions(), python_version_spec
    )
    if compatible_version is not None:
        logging.info(
            f'A Python {compatible_version} found online which is compatible with '
            f'the specification of {python_version_spec}. It will be installed locally '
            f'and used to create a virtual environment.'
        )
        return compatible_version

    raise RuntimeError(
        f'Unfortunately Python {python_version_spec} is not available '
        f'neither locally (check {str(_BASE_ENVS_DIR)}) nor online (check '
        f'https://www.nuget.org/packages/python).'
    )


def base_venv_exists(python_version: str) -> bool:
    """
    Verifies if the base virtual environment of the specified Python version exists.

    The base environment stored in `python_version` subdirectory of `_BASE_ENVS_DIR`
    is expected to contain Python of the same version.

    Args:
        python_version: A Python version to check.

    Returns:
        `True` if the base virtual environment exists and contains a Python executable.
    """
    return venv_exists(_BASE_ENVS_DIR / python_version)


def venv_is_compatible(venv_dir: Path, python_version_spec: str) -> bool:
    """
    Verifies if the venv is compatible with the Python version specification.

    Args:
        venv_dir: A path to check.

        python_version_spec: A Python version specification.

    Returns:
        `True` if the virtual environment exists and contains a Python version that is
        compatible with the `python_version_spec`.
    """
    venv_python_version = get_venv_python_version(venv_dir)
    return python_version_matches_spec(venv_python_version, python_version_spec)


def get_venv_executable(venv_dir: Path, executable: str) -> Path:
    """
    Return the full path to an executable inside a given virtual environment.

    Args:
        venv_dir: Path to the directory containing the virtual environment.

        executable: Name of the executable.

    Returns:
        Full path to an executable inside the virtual environment.

    Raises:
        FileNotFoundError:  When the executable could not be found.
    """

    search_path = [str(venv_dir / p) for p in _VENV_BIN_SEARCH_DIRS]
    venv_executable = shutil.which(cmd=executable, path=os.pathsep.join(search_path))

    if venv_executable is None:
        raise FileNotFoundError('The virtual environment executable could not be found')

    return Path(venv_executable)


def get_venv_executable_optional(venv_dir: Path, executable: str) -> Optional[Path]:
    """
    Return the full path to an executable inside a given virtual environment.

    Args:
        venv_dir: Path to the directory containing the virtual environment.

        executable: Name of the executable.

    Returns:
        Full path to an executable inside the virtual environment, or None if the
            executable is not found.
    """
    try:
        venv_executable = get_venv_executable(venv_dir=venv_dir, executable=executable)
    except FileNotFoundError:
        return None
    return venv_executable


def get_venv_python(venv_dir: Path) -> Path:
    """
    Return the Python executable inside a given virtual environment.

    Args:
        venv_dir: Path to the directory containing the virtual environment.

    Returns:
        Path: Full path to the Python executable inside the virtual environment.

    Raises:
        FileNotFoundError:  When the executable could not be found.
    """
    return get_venv_executable(venv_dir=venv_dir, executable=Path(sys.executable).name)


def venv_python_exists(venv_dir: Path) -> bool:
    """
    Return whether the Python executable exists in a given virtual environment.

    Args:
        venv_dir: Path to the directory containing the virtual environment.

    Returns:
        bool: True if the Python executable exists in the virtual environment.
    """
    venv_executable = get_venv_executable_optional(
        venv_dir=venv_dir, executable=Path(sys.executable).name
    )
    return venv_executable is not None


def get_base_python(python_version: str) -> Path:
    """
    Return a base Python executable of a certain version.

    On Windows this function expects the base virtual environment with the required
    Python version to be present and looks for Python there.

    On other systems only system Python version is supported.

    Args:
        python_version: A version of the base python to look for.

    Returns:
        Path: Full path to the base Python executable.

    Raises:
        EnvironmentError: On non-Windows OS if the `python_version` is different from
            the system Python version.
    """
    if sys.platform != 'win32':
        if version_matches_spec(_THIS_PYTHON_VERSION, python_version):
            return sys.executable
        else:
            raise EnvironmentError(
                f'Custom Python version is not supported on your platform '
                f'({sys.platform}). You can only use system Python '
                f'{_THIS_PYTHON_VERSION}.'
            )

    return get_venv_python(_BASE_ENVS_DIR / python_version)


def run_python(python_executable: Path, *args: str, **kwargs: Dict[str, Any]):
    """
    A convenience function to run a python command.

    Args:
        python_executable: A path to the python executable to call.

        args: Any arguments to pass to the call, e.g.: '-m', 'pip', 'list' or
            '-m pip list'.

        kwargs: Any keyword arguments to pass to the underlying `subprocess` call, e.g.
            stdin, stdout and stderr.
    """
    check_call(python_executable, *args, **kwargs)


def run_pip(python_executable: Path, *args: Any, **kwargs: Dict[str, Any]):
    """
    A convenience function to run a pip command.

    Functionally it's equalent to `python -m pip` call.

    Args:
        python_executable: A path to the python executable to call.

        args: Any arguments to pass to `pip`, e.g.: 'list'.

        kwargs: Any keyword arguments to pass to the underlying `subprocess` call, e.g.
                stdin, stdout and stderr.
    """
    run_python(python_executable, '-m', 'pip', *args, **kwargs)


def get_pip_packages(python_executable: Path) -> Dict[str, str]:
    """
    Retrieve a list of packages installed by pip.

    It gets only the versions of the packages reported as `package==version`. The other
    formats (e.g. the ones installed from git or local files are ignored).

    Args:
        python_executable: A path to the Python executable to check.

    Returns:
        A dictionary where the key corresponds to the name of the package and the value
            to its version.

    Raises:
        ValueError: If the package format is incorrect.
    """
    packages = check_output(python_executable, '-m', 'pip', 'freeze').split()

    # The output of `freeze` contains a package per line in a `package==version`
    # format, but there are exceptions (e.g. packages installed from git reviesion) -
    # we filter those out.
    package_dict = {}
    for p in packages:
        if '==' in p:
            try:
                name, version = p.split('==')
            except ValueError:
                raise ValueError(
                    f'Incorrect package format: {p}. Package format cannot have more '
                    f'than one `==`.'
                )
            package_dict[name] = version

    return package_dict


def get_python_version(python_executable: Path) -> str:
    """
    Retrieve a version of the Python executable.

    Args:
        python_executable: A Python to check the version for.

    Returns:
        A version in a form of '3.10.11'.
    """
    script = (
        "from sys import version_info as v; print(f'{v.major}.{v.minor}.{v.micro}')"
    )

    return check_output(python_executable, '-c', script)


def get_venv_python_version(venv_dir: Path) -> str:
    """
    Retrieve a version of Python in a certain virtual environment.

    Args:
        venv_dir: A directory with the virtual environment.

    Returns:
        A version of the virtual environment Python executable in a form of '3.10.11'.
    """
    vpython = get_venv_python(venv_dir)
    return get_python_version(vpython).strip()


def create_base_venv(target_dir: Path, python_version: str):
    """
    Create a base virtual environment with the required Python version.

    On Windows this function installs only Python inside the required folder. It doesn't
    need for the folder to exist and it doesn't check if the folder is empty, so it will
    overwrite any files already there.

    Args:
        target_dir: A directory where the environment should be created.

        python_version: A Python version that needs to be installed.

    Raises:
        EnvironmentError: If running on non-Windows OS.
        RuntimeError: If the required Python version is not available for installation.
    """
    if sys.platform != 'win32':
        raise EnvironmentError(
            f'Custom Python version is not supported on your platform '
            f'({sys.platform}). You can only use system Python '
            f'{_THIS_PYTHON_VERSION}.'
        )

    try:
        versions_url = f'{_NUGET_PACKAGE_BASE_URL}/python/index.json'
        with urlopen(versions_url) as response:
            available_versions = json.loads(response.read())['versions']
    except Exception as e:
        raise RuntimeError(
            f'Error retrieving a list of available Python versions from {versions_url}.'
            f'Exact error: {e}.'
        )

    if python_version not in available_versions:
        raise RuntimeError(
            f'Unfortunately Python {python_version} is not available for installation.'
            f'For the full list of versions please visit '
            f'https://www.nuget.org/packages/python.'
        )

    target_dir.mkdir(parents=True, exist_ok=True)

    # Download the required Python from Nuget.
    nuget_dir = target_dir / 'nuget'
    nuget_dir.mkdir(exist_ok=True)
    try:
        download_url = (
            f'{_NUGET_PACKAGE_BASE_URL}/python/{python_version}/python.'
            f'{python_version}.nupkg'
        )
        outfile = nuget_dir / f'python.{python_version}.nupkg'

        with urlopen(download_url) as response:
            outfile.write_bytes(response.read())
    except Exception as e:
        raise RuntimeError(
            f'Error downloading Python {python_version} from {download_url}. '
            f'Exact error: {e}.'
        )

    # Nuget package is just a zip archive, so we simply unzip it and move the contents
    # of the 'tools' folder into the target directory.
    extract_dir = nuget_dir / 'unzip'
    with zipfile.ZipFile(outfile, 'r') as zf:
        zf.extractall(extract_dir)
        for to_move in (extract_dir / 'tools').iterdir():
            to_move.rename(target_dir / to_move.name)


def ensure_base_python(python_version: str):
    """
    Ensures that the base virtual environment of a certain Python version exists.

    On Windows the base virtual environment will be created if it doesn't exist yet.

    A successful execution of this function means that `get_base_python(python_version)`
    can be called safely.

    Args:
        python_version: A required Python version.

    Raises:
        EnvironmentError: If running on non-Windows OS and requiring a Python version
            different from the system one.
    """
    if sys.platform != 'win32':
        if python_version == _THIS_PYTHON_VERSION:
            return
        else:
            raise EnvironmentError(
                f'Custom Python version is not supported on your platform '
                f'({sys.platform}). You can only use system Python '
                f'{_THIS_PYTHON_VERSION}.'
            )

    if base_venv_exists(python_version):
        return

    create_base_venv(_BASE_ENVS_DIR / python_version, python_version)


def setup_pip_config_file(venv_dir: Path, pip_config: Dict[str, str]) -> Optional[Path]:
    """
    Setup the pip config file for the virtual environment.

    If the `pip_config` argument is provided, the contents will be copied to the
    [global] section of the pip.conf/pip.ini (win/linux,macos) file inside a virtual
    environment. This can be used to provide any extra parameters to pip,
    e.g. `extra-index-url`.

    If the `pip_config` is `None` the venv pip configuration file will be removed from
    the virtual environment as well.

    Args:
        venv_dir: A directory with the virtual environment to initialize.

        pip_config: A dictionary with `pip` options.

    Returns:
        A path to the pip configuration file if created, `None` otherwise.
    """
    pip_conf_path = venv_dir / _PIP_CONF

    if pip_config is None:
        if pip_conf_path.exists():
            pip_conf_path.unlink()
        return None

    pip_conf = ConfigParser()
    pip_conf.add_section('global')
    for key, value in pip_config.items():
        pip_conf.set(section='global', option=key, value=value)

    with pip_conf_path.open('w') as fid:
        pip_conf.write(fid)

    return pip_conf_path


def clear_venv(venv_dir: Path):
    """
    Remove the virtual environment.

    Args:
        venv_dir: A directory containina a virtual environment.
    """
    shutil.rmtree(venv_dir)


def create_venv(venv_dir: Path, dsvenv_config: DSVenvConfig):
    """
    Create a bare virtual environment in a given directory.

    The function ensures that the base Python of the required version exists in the
    system and creates a virtual environment out of it at a specified location.

    Args:
        venv_dir: A directory where the virtual environment should be created.

        dsvenv_config: A configuration containing various venv options.
    """
    python_version_spec = dsvenv_config.python_version
    python_version = resolve_python_version_spec(python_version_spec)
    ensure_base_python(python_version=python_version)

    # Create a virtual environment
    base_python = get_base_python(python_version=python_version)
    run_python(base_python, '-m', 'venv', f'{venv_dir}')


def initialize_venv(
    venv_dir: Path,
    dsvenv_config: DSVenvConfig,
    pip_config: Dict[str, str],
    requirements: List[Path],
):
    """
    Initialize a virtual environment by installing the necessary requirements.

    The requirements installation goes in stages:

    1. Mandatory requirements (e.g. pip, setuptools) and present Azure PyPi
        requirements (artifacts-keyring) as specified in setup.cfg.
    2. Virtual environment pip configuration file is updated.
    3. All the rest required packages from setup.cfg.
    4. All the requirements files.

    Args:
        venv_dir:  Path to a virtual environment.

        dsvenv_config: additional venv options. All the requirements from
            `_MANDATORY_DSVENV_REQUIRES` must be present in the config `requires`
            section.

        pip_config: Additional `pip` options for the environment.

        requirements: A list of paths to the existing requirements files.
    """

    # Get the venv python executable
    vpython = get_venv_python(venv_dir)
    requires = dsvenv_config.requires

    # Ensure that all the required reqs will be installed.
    mandatory_reqs = [requires[r] for r in _MANDATORY_DSVENV_REQUIRES]

    # Ensure recent versions of artifacts-keyring (so that we can use an Azure-hosted
    # PyPi server).
    mandatory_azure_artifacts_reqs = [
        requires[r] for r in _MANDATORY_AZURE_ARTIFACTS_REQUIRES if r in requires
    ]

    # The --isolated flag is necessary to make sure we don't use any information from
    # a pip configuration file.
    run_pip(
        vpython,
        'install',
        '--isolated',
        '--upgrade',
        *mandatory_reqs,
        *mandatory_azure_artifacts_reqs,
    )

    # Ensure that a pip.ini or pip.conf file is installed if necessary.
    # (!)This needs to be done after keyring and artifacts-keyring is installed.
    setup_pip_config_file(venv_dir=venv_dir, pip_config=pip_config)

    # And now we just install all the requirements from the configuration file (it
    # contains pip, setuptools, etc. again, but this won't cause any harm).
    # Additionally it may resolve a problem with artifacts-keyring not showing the
    # authentication prompt for the Azure PyPi (sometimes installing requirements.txt
    # becomes stuck, while installing any packages directly works).
    # The bug looks awfully similar to this one:
    # https://github.com/microsoft/artifacts-keyring/issues/25
    run_pip(vpython, 'install', *requires.values())

    # Add a `-r` option before each requirement file.
    if requirements:
        vpython = get_venv_python(venv_dir)
        requirement_args = [a for r in requirements for a in ['-r', r]]
        run_pip(vpython, 'install', *requirement_args)


def verify_venv(venv_dir: Path, azure_pipelines_config: AzurePipelinesConfig):
    """
    Perform a sanity check on the interpreter executing this script.

    Verify if the environment that is being used is based on the correct version of
    Python and `dsvenv` (the ones stored in `azure.yml` if present).

    The function has no side effects and only writes warnings about any inconsistencies
    to the log.

    Args:
        venv_dir: A path to the virtual environment directory.

        azure_pipelines_config: An Azure pipeline configuration
            to verify the environment against (e.g. python version, dsvenv version).
    """
    required_python, required_dsvenv = azure_pipelines_config
    existing_python = get_venv_python_version(venv_dir)
    existing_dsvenv = __version__

    if required_python is not None:
        if not version_matches_spec(existing_python, required_python):
            logging.warning(
                f'The virtual environment Python version ({existing_python}) is not the'
                f' same as the version specified in Azure pipelines configuration '
                f'({required_python}).'
            )

    if required_dsvenv is not None:
        if not version_matches_spec(existing_dsvenv, required_dsvenv):
            logging.warning(
                f'The current dsvenv version ({existing_dsvenv}) is not the same as '
                f'the version specified in Azure pipelines configuration '
                f'({required_dsvenv}).'
            )


def install_pre_commit_hooks(venv_dir: Path):
    """
    Install the `pre-commit` hooks.

    This function assumes that when pre-commit hooks are configured for the repo, the
    `requirements.txt` file contains a pre-commit requirement
    (eg. `pre-commit==<version>`).

    Args:
        venv_dir: The path to the virtual environment directory.

    Raises:
        EnvironmentError: When the pre-commit package is not installed.
    """
    vpython = get_venv_python(venv_dir)

    # Verify if pre-commit package itself is installed.
    if 'pre-commit' not in get_pip_packages(vpython):
        raise EnvironmentError(
            'The pre-commit package cannot be found in your virtual environment.\n'
            'Make sure to specify a pre-commit requirement in the '
            '`requirements.txt` file (eg. `pre-commit==<version>`).'
        )

    # Then actually install the hooks.
    run_python(vpython, '-m', 'pre_commit', 'install')


def ensure_venv(
    venv_dir: Path,
    dsvenv_config: DSVenvConfig,
    pip_config: Dict[str, str],
    requirements: List[Path],
    azure_pipelines_config: AzurePipelinesConfig,
    clear: bool,
    should_install_pre_commit_hooks: bool,
):
    """
    This function ensures existing of a compatible virtual environment.

    The existing virtual environment will be removed only if explicitly requested.

    The function will allow to proceed with the existing environment only if its Python
    is compatible with the required python version.

    A pip configuration from the additional configuration file will be copied to the
    virtual environment pip configuration file.

    Any requirements required will be installed in the virtual environment.

    The environment is verified to be in sync with `azure_pipelines_config` (used for
    CI builds of the package) if it exists.

    The pre-commit hooks will be created if requested.

    Args:
        venv_dir: A directory for the virtual environment should exist.

        dsvenv_config: An additional configuration for the venv itself, e.g. Python
            version, additional build packages.

        pip_config: A pip configuration for the virtual environment.

        requirements: A list of paths to the files with requirements that will be
            installed in the environment.

        azure_pipelines_config: An Azure pipelines config to verify the environment
            against.

        clear: If `True`, any existing environment will be removed.

        should_install_pre_commit_hooks: If `True` the pre-commit hooks will be
            configured according to the `.pre-commit-config.yaml` file.

    Raises:
        EnvironmentError: If the existing environment is not compatible with the
            required Python version.
    """
    if venv_exists(venv_dir) and clear:
        logging.warning(
            f'Existing environment at {venv_dir} will be removed as requested'
            f' by --clear flag.'
        )
        clear_venv(venv_dir)

    python_version_spec = dsvenv_config.python_version
    if venv_exists(venv_dir):
        if not venv_is_compatible(venv_dir, python_version_spec):
            raise EnvironmentError(
                f'A virtual environment of Python {get_venv_python_version(venv_dir)} '
                f'already exists at {venv_dir} and it is not compatible with the '
                f'requested Python {python_version_spec}. Please use --clear option to'
                f' automatically delete the existing environment or remove it manually.'
            )
        else:
            logging.info(f'Reusing existing virtual environment at {venv_dir}.')
    else:
        logging.info(
            f'The virtual environment compatible with Python {python_version_spec} will'
            f' be created at {venv_dir}.'
        )
        create_venv(venv_dir, dsvenv_config)

    initialize_venv(venv_dir, dsvenv_config, pip_config, requirements)

    verify_venv(venv_dir, azure_pipelines_config)

    if should_install_pre_commit_hooks:
        install_pre_commit_hooks(venv_dir)


def parse_setup_cfg(
    setup_cfg_path: Path, python_version: str, venv_dir: Path
) -> Tuple[Optional[PipConfig], DSVenvConfig]:
    """
    Parse the configuration file for pip and dsvenv config.

    The purpose of this function is to contain a lot of ugly code resulting in a fact
    that dsvenv operates over multiple config files (and command line arguments in
    addition), some of which are implicit and some may reference others.

    If the `setup_cfg_path` exists, it will look for 2 things:
    - `pip_config` section - additional pip configuration for the venv;
    - `dsvenv` section - a configuration for the venv itself.

    To complete `dsvenv` it then does the following:

    1. Resolves the python version in order of priority:
        - `python_version`;
        - a version from the configuration file;
        - a version from existing environment at `venv_dir`
        - a default version.

    2. parses any `requires` packages and resolves defaults and `None` packages.

    Args:
        setup_cfg_path: A path to the configuration file.

        python_version: Any explicitly provided Python version.

        venv_dir: A venv directory.

    Returns:
        pip and dsvenv configurations.
    """

    def prepare_requirements(requirements: List[str]) -> Dict[str, Requirement]:
        """
        A function that parses a requirement string and resolves defaults.

        First we use the `setuptools` functionality to parse the requirement specs
        and merge them with the default requirements (overwriting any defaults).

        Then we throw away any requirements with '===None' spec allowing to override
        even the defaults.

        Args:
            requirements: A list of pip requirements.

        Returns:
            A dictionary, where keys are the package names and the values are full
            requirement specs, e.g.: { 'dsbuild': Requirement('dsbuild==0.0.7') }.
        """
        # Parse all the reqs together with specs
        parsed_requirements = _parse_requirements(requirements)

        # Now combine them together allowing `requirements` to override any defaults.
        parsed_requirements = {**_DEFAULT_DSVENV_REQUIRES, **parsed_requirements}

        # And finally throw away anything with a spec of '===None'
        parsed_requirements = {
            k: v
            for k, v in parsed_requirements.items()
            if str(v.specifier) != '===None'
        }

        return parsed_requirements

    # Setting sensible defaults for the results
    # `dsvenv_config` will be used later to create a DsVenvConfig named tuple, which
    # already has the default values for the missing values, that's why we don't need
    # to add anything.
    pip_config = None
    dsvenv_config: Dict[str, Union[str, Path, Dict[str, Requirement]]] = {}

    if setup_cfg_path is not None:
        setup_cfg = ConfigParser()
        setup_cfg.read(setup_cfg_path)

        # Read pip config if it exists
        try:
            pip_config = dict(setup_cfg.items('pip_config'))
        except NoSectionError:
            pass

        try:
            dsvenv_config_full = dict(setup_cfg.items('dsvenv'))
            dsvenv_config = {
                k: v for k, v in dsvenv_config_full.items() if k in DSVenvConfig._fields
            }

            if dsvenv_config.keys() != dsvenv_config_full.keys():
                unknown_options = list(dsvenv_config_full.keys() - dsvenv_config.keys())
                logging.warning(
                    f'The following options specified in "dsvenv" section of the '
                    f'configuration file {setup_cfg_path} are unknown and will be'
                    f' ignored: {unknown_options}.'
                )

            if 'azure_pipelines_yml' in dsvenv_config:
                dsvenv_config['azure_pipelines_yml'] = Path.cwd() / str(
                    dsvenv_config['azure_pipelines_yml']
                )

            # Prepare the requirements
            # Since INI is not TOML, it cannot resolve a list option into a Python list.
            # Instead we receive it as a multiline string of format "[\n'dsbuild'\n]".
            # That's why we first convert it into a valid list.
            dsvenv_config['requires'] = prepare_requirements(
                ast.literal_eval(str(dsvenv_config.get('requires', '[]')))
            )
        except NoSectionError:
            pass

    # And now we finally resolve the Python version:
    if python_version is not None:
        dsvenv_config['python_version'] = python_version
    elif 'python_version' not in dsvenv_config:
        if venv_exists(venv_dir):
            dsvenv_config['python_version'] = get_venv_python_version(venv_dir)

    dsvenv_conf = DSVenvConfig(**dsvenv_config)  # type: ignore[arg-type, return-value]
    return pip_config, dsvenv_conf


def parse_azure_pipelines(azure_pipelines_path: Optional[Path]) -> AzurePipelinesConfig:
    """
    Parse the Azure pipelines file if it exists.

    If `azure_pipelines_path` is explicitly `None` the function will check if either
    default `azure-pipelines.yml` or legacy `azure.yml` exists and use that one instead.

    Args:
        azure_pipelines_path: A path to Azure pipelines file.

    Return:
        Azure pipelines configuration.
    """
    if azure_pipelines_path is None:
        return AzurePipelinesConfig()

    if azure_pipelines_path == _LEGACY_AZURE_PIPELINES_YAML:
        logging.warning(
            f'It seems that you use a legacy "azure.yml" Azure configuration file '
            f'at {azure_pipelines_path}. Please rename it to "azure-pipelines.yml" '
            f'to silence this warning (do not forget to point the DevOps pipeline '
            f'to the new file).'
        )

    azure_pipeline_yaml = azure_pipelines_path.read_text()

    match = re.search(r'python_version:\s+(\S+)', azure_pipeline_yaml)
    azure_python_version = match.group(1) if match is not None else None

    match = re.search(r'dsvenv_version:\s+(\S+)', azure_pipeline_yaml)
    azure_dsvenv_version = match.group(1) if match is not None else None

    return AzurePipelinesConfig(azure_python_version, azure_dsvenv_version)


def parse_args() -> Namespace:
    """
    Parse the input argumens and validate them.

    Parses the argument according to the parser configuration below providing a few
    tweaks.

    If no requirement files were provided and `requirements.txt` exists it will be used
    by default. Any explicitly provided file must exist.

    If no config file was provided and `setup.cfg` exists it will be used by default. If
    provided explicitly the file must exist.

    Return:
        All the args parsed.

    Raises:
        FileNotFoundError: If any of explicitly provided files does not exist.
        ValueError: If any of the mandatory requirements is missing.
        RuntimeError: If the pre-commit hooks are requested and `git` is not available.
    """
    parser = ArgumentParser(
        description=(
            'Create and initialize a virtual environment based on a requirements file. '
            'If a `.pre-commit-config.yaml` is present, pre-commit hooks will be '
            'installed.'
        ),
        prog='dsvenv',
    )
    parser.add_argument(
        '--version', '-v', action='version', version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '--venv-dir',
        '-vd',
        type=Path,
        default=Path.cwd() / '.venv',
        help='Directory containing the virtual environment.',
    )
    parser.add_argument(
        '--python-version',
        '-p',
        help=(
            'The desired Python version of the virtual environment. This can also be a '
            'specifier e.g. ~=3.10 or >=3.8,<3.9. If not provided, the version will be '
            'resolved from the configuration file or the existing environment.'
        ),
    )
    parser.add_argument(
        '--requirement',
        '-r',
        dest='requirements',
        type=Path,
        default=[_DEFAULT_REQUIREMENTS_TXT] if _DEFAULT_REQUIREMENTS_TXT else [],
        action='append',
        help='Optional path to the requirements file to be used.',
    )
    parser.add_argument(
        '--clear',
        '-c',
        default=False,
        action='store_true',
        help=(
            'If given, remove an already existing virtual environment before '
            'initializing it with the provided requirements.'
        ),
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=_DEFAULT_SETUP_CFG,
        help=(
            'Path to the configuration file (setup.cfg by default). The [pip_config] '
            'section will be written to a pip configuration file inside the virtual '
            'environment (if the section is not present, this file will be removed). '
            'The [dsvenv] section may contain the following options: "python_version" '
            '(specifies the desired venv Python version), "azure_pipelines_yml" (a name'
            ' of the Azure pipelines file) and "requires" (a list of pip package '
            'specifications required for the build, e.g. "dsbuild" or "pip==20.0.1"). '
            '"requires" syntax comes from pyproject.toml. It additionally allows to '
            'specify "===None" as a package version, which means that the package '
            'will not be installed during the environment initialization even if '
            'dsvenv does it by default (e.g. "dsbuild===None" prevents the default '
            'installation of "dsbuild").'
        ),
    )
    parser.add_argument(
        '--no-pre-commit',
        '--no-install-pre-commit-hooks',
        dest='install_pre_commit_hooks',
        default=(_DEFAULT_PRE_COMMIT_YAML is not None),
        action='store_false',
        help='If given, pre-commit hooks will not be installed.',
    )

    args = parser.parse_args()

    for r in args.requirements:
        if not r.exists():
            raise FileNotFoundError(
                f'The requirements file "{r}" provided with --requirement flag does'
                f' not exist.'
            )

    if args.config is not None:
        if not args.config.exists():
            raise FileNotFoundError(
                f'The configuration file "{args.config}" provided with --config-file'
                f' flag does not exist.'
            )

    args.pip_config, args.dsvenv_config = parse_setup_cfg(
        args.config, args.python_version, args.venv_dir
    )

    if args.dsvenv_config.azure_pipelines_yml is not None:
        if not args.dsvenv_config.azure_pipelines_yml.exists():
            raise FileNotFoundError(
                f'The Azure pipelines file "{args.dsvenv_config.azure_pipelines_yml}" '
                f'does not exist.'
            )

    # Verify if any mandatory requirements are missing
    missing_reqs = [
        r for r in _MANDATORY_DSVENV_REQUIRES if r not in args.dsvenv_config.requires
    ]
    if missing_reqs:
        raise ValueError(
            f'The following requirements are mandatory and cannot be excluded using'
            f' the "===None" syntax: {missing_reqs}.'
        )

    args.azure_pipelines_config = parse_azure_pipelines(
        args.dsvenv_config.azure_pipelines_yml
    )

    # Check if git exists if the pre-commit hooks are needed
    if args.install_pre_commit_hooks:
        if shutil.which('git') is None:
            raise RuntimeError(
                '"git" executable is not available, while the pre-commit hooks are '
                'requested to be installed. Either ensure you have git installed or '
                f'disable pre-commit hooks by removing the "{_DEFAULT_PRE_COMMIT_YAML}"'
                'configuration file or using "--no-pre-commit" option.'
            )

    return args


def error_print(func: Callable) -> Callable:
    """
    This decorator function captures all exceptions of `func` and displays them nicely.

    First the traceback will be displayed, then the error message.
    """

    def inner():
        try:
            func()
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error('')
            logging.error('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            logging.error('!!! DSVENV HAS ENCOUNTERED AN ERROR !!!')
            logging.error('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            logging.error('')
            logging.error(e)
            logging.error('')
            sys.exit(1)

    return inner


@error_print
def main():
    setup_logging()

    args = parse_args()

    ensure_venv(
        venv_dir=args.venv_dir,
        dsvenv_config=args.dsvenv_config,
        pip_config=args.pip_config,
        requirements=args.requirements,
        azure_pipelines_config=args.azure_pipelines_config,
        clear=args.clear,
        should_install_pre_commit_hooks=args.install_pre_commit_hooks,
    )


if __name__ == '__main__':
    main()
