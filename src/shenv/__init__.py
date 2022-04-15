#!/usr/bin/env python3
# coding=utf-8
"""
ShEnv Package
"""
__all__ = (
    'HELP_OPTIONS',
    'LINUX',
    'MACOS',

    'AnyPath',
    'ExcType',
    'IPAddressType',

    'cli_invoke',

    'EnvBase',
    'EnvAction',
    'EnvConfig',
    'EnvDynamic',
    'EnvJetBrains',
    'EnvPython',
    'EnvSecrets',
    'EnvSystem',
    'EnvUnix',
    'Env',

    'parse_env',
    'parse_str',
    'version',
)
import ipaddress
import importlib.metadata
import os
import sys
from dataclasses import dataclass
from dataclasses import field
from dataclasses import InitVar
from ipaddress import IPv4Address
from ipaddress import IPv6Address
from os import PathLike
from typing import Any
from typing import AnyStr
from typing import IO
from typing import Optional
from typing import Type
from typing import Union

try:
    from ppath import Path
except ImportError:
    from pathlib import Path

from furl import furl
from typer import Argument
from typer import Typer
from typer.testing import CliRunner

ENV_PARSE_AS_INT_NAME = ('PID', 'PPID',)
ENV_PARSE_AS_INT_SUFFIX = ('_ATTEMPT', '_ID', '_GID', '_JOBS', '_NUMBER', '_PORT', '_UID',)

LINUX = sys.platform == "linux"
MACOS = sys.platform == "darwin"
HELP_OPTIONS = dict(help_option_names=['-h', '--help'])

AnyPath = Union[Path, PathLike, AnyStr, IO[AnyStr]]
ExcType = Union[Type[Exception], tuple[Type[Exception], ...]]
IPAddressType = Union[IPv4Address, IPv6Address]

cli_invoke = CliRunner().invoke

app = Typer(add_completion=False, context_settings=HELP_OPTIONS, name=Path(__file__).parent.name)


@dataclass
class EnvBase:
    """Base Environment Variables Class"""
    parsed: InitVar[bool] = True

    def __post_init__(self, parsed: bool) -> None:
        """
        Instance of Env class

        Args:
            parsed: Parse the environment variables using :func:`mreleaser.parse_str`,
                except :func:`Env.as_int` (default: True)
        """
        self.__dict__.update({k: self.as_int(k, v) for k, v in os.environ.items()} if parsed else os.environ)

    def __contains__(self, item):
        return item in self.__dict__

    def __getattr__(self, name: str) -> Optional[str]:
        if name in self:
            return self.__dict__[name]
        return None

    def __getattribute__(self, name: str) -> Optional[str]:
        if hasattr(self, name):
            return super().__getattribute__(name)
        return None

    def __getitem__(self, item: str) -> Optional[str]:
        return self.__getattr__(item)

    @classmethod
    def as_int(cls, key: str, value: str = '') -> Optional[Union[bool, Path, furl, int, IPAddressType, str]]:
        """
        Parse as int if environment variable should be forced to be parsed as int checking if:

            - has value,
            - key in :data:`Env._parse_as_int` or
            - key ends with one of the items in :data:`Env._parse_as_int_suffix`.

        Args
            key: Environment variable name.
            value: Environment variable value (default: '').

        Returns:
            int, if key should be parsed as int and has value, otherwise according to :func:`parse_str`.
        """
        convert = False
        if value:
            if key in ENV_PARSE_AS_INT_NAME:
                convert = True
            else:
                for item in ENV_PARSE_AS_INT_SUFFIX:
                    if key.endswith(item):
                        convert = True
                        break
        return int(value) if convert and value.isnumeric() else parse_str(value)


# noinspection LongLine
@dataclass
class EnvAction(EnvBase):
    """
    GitHub Actions Environment Variables Class

    See Also: `Environment variables
    <https://docs.github.com/en/enterprise-cloud@latest/actions/learn-github-actions/environment-variables>`_

    If you need to use a workflow run's URL from within a job, you can combine these environment variables:
        ``$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID``

    If you generate a value in one step of a job, you can use the value in subsequent ``steps`` of
        the same job by assigning the value to an existing or new environment variable and then writing
        this to the ``GITHUB_ENV`` environment file, see `Commands
        <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflow-commands-for-github-actions/#setting-an-environment-variable>`_.

    If you want to pass a value from a step in one job in a ``workflow`` to a step in another job in the workflow,
        you can define the value as a job output, see `Syntax
        <https://docs.github.com/en/enterprise-cloud@latest/actions/learn-github-actions/workflow-syntax-for-github-actions#jobsjob_idoutputs>`_.
    """

    CI: Optional[Union[bool, str]] = field(default=None, init=False)
    """
    Always set to ``true`` in a GitHub Actions environment.
    """

    GITHUB_ACTION: Optional[str] = field(default=None, init=False)
    """
    The name of the action currently running, or the step `id
<https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsid>`_.
    
    For example, for an action, ``__repo-owner_name-of-action-repo``.
    
    GitHub removes special characters, and uses the name ``__run`` when the current step runs a script without an id. 

    If you use the same script or action more than once in the same job, 
    the name will include a suffix that consists of the sequence number preceded by an underscore. 
    
    For example, the first script you run will have the name ``__run``, and the second script will be named ``__run_2``. 

    Similarly, the second invocation of ``actions/checkout`` will be ``actionscheckout2``.
    """

    GITHUB_ACTION_PATH: Optional[Union[Path, str]] = field(default=None, init=False)
    """
    The path where an action is located. This property is only supported in composite actions. 
    
    You can use this path to access files located in the same repository as the action. 
    
    For example, ``/home/runner/work/_actions/repo-owner/name-of-action-repo/v1``.
    """

    GITHUB_ACTION_REPOSITORY: Optional[str] = field(default=None, init=False)
    """
    For a step executing an action, this is the owner and repository name of the action. 
    
    For example, ``actions/checkout``.
    """

    GITHUB_ACTIONS: Optional[Union[bool, str]] = field(default=None, init=False)
    """
    Always set to ``true`` when GitHub Actions is running the workflow. 
    
    You can use this variable to differentiate when tests are being run locally or by GitHub Actions.
    """

    GITHUB_ACTOR: Optional[str] = field(default=None, init=False)
    """
    The name of the person or app that initiated the workflow. 
    
    For example, ``octocat``.
    """

    GITHUB_API_URL: Optional[Union[furl, str]] = field(default=None, init=False)
    """
    API URL. 
    
    For example: ``https://api.github.com``.
    """

    GITHUB_BASE_REF: Optional[str] = field(default=None, init=False)
    """
    The name of the base ref or target branch of the pull request in a workflow run. 
    
    This is only set when the event that triggers a workflow run is either ``pull_request`` or ``pull_request_target``. 
    
    For example, ``main``.
    """

    GITHUB_ENV: Optional[Union[Path, str]] = field(default=None, init=False)
    """
    The path on the runner to the file that sets environment variables from workflow commands. 
    
    This file is unique to the current step and changes for each step in a job. 
    
    For example, ``/home/runner/work/_temp/_runner_file_commands/set_env_87406d6e-4979-4d42-98e1-3dab1f48b13a``. 
    
    For more information, see `Workflow commands for GitHub Actions.
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-commands-for-github-actions#setting-an-environment-variable>`_
    """

    GITHUB_EVENT_NAME: Optional[str] = field(default=None, init=False)
    """
    The name of the event that triggered the workflow. 
    
    For example, ``workflow_dispatch``.
    """

    GITHUB_EVENT_PATH: Optional[Union[Path, str]] = field(default=None, init=False)
    """
    The path to the file on the runner that contains the full event webhook payload. 
    
    For example, ``/github/workflow/event.json``.
    """

    GITHUB_GRAPHQL_URL: Optional[Union[furl, str]] = field(default=None, init=False)
    """
    Returns the GraphQL API URL. 
    
    For example: ``https://api.github.com/graphql``.
    """

    GITHUB_HEAD_REF: Optional[str] = field(default=None, init=False)
    """
    The head ref or source branch of the pull request in a workflow run. 
    
    This property is only set when the event that triggers a workflow run is either 
    ``pull_request`` or ``pull_request_target``.
    
    For example, ``feature-branch-1``.
    """

    GITHUB_JOB: Optional[str] = field(default=None, init=False)
    """
    The `job_id
    <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflow-syntax-for-github-actions#jobsjob_id>`_ 
    of the current job. 
    
    For example, ``greeting_job``.
    """

    GITHUB_PATH: Optional[Union[Path, str]] = field(default=None, init=False)
    """
    The path on the runner to the file that sets system PATH variables from workflow commands. 
    This file is unique to the current step and changes for each step in a job. 
    
    For example, ``/home/runner/work/_temp/_runner_file_commands/add_path_899b9445-ad4a-400c-aa89-249f18632cf5``. 
    
    For more information, see 
    `Workflow commands for GitHub Actions.
     <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-commands-for-github-actions#adding-a-system-path>`_
    """

    GITHUB_REF: Optional[str] = field(default=None, init=False)
    """
    The branch or tag ref that triggered the workflow run.
    
    For branches this is the format ``refs/heads/<branch_name>``, 
    for tags it is ``refs/tags/<tag_name>``, 
    and for pull requests it is ``refs/pull/<pr_number>/merge``. 
    
    This variable is only set if a branch or tag is available for the event type. 
    
    For example, ``refs/heads/feature-branch-1``.
    """

    GITHUB_REF_NAME: Optional[str] = field(default=None, init=False)
    """
    The branch or tag name that triggered the workflow run. 
    
    For example, ``feature-branch-1``.
    """

    GITHUB_REF_PROTECTED: Optional[Union[bool, str]] = field(default=None, init=False)
    """
    ``true`` if branch protections are configured for the ref that triggered the workflow run.
    """

    GITHUB_REF_TYPE: Optional[str] = field(default=None, init=False)
    """
    The type of ref that triggered the workflow run. 
    
    Valid values are ``branch`` or ``tag``.
    
    For example, ``branch``.
    """

    GITHUB_REPOSITORY: Optional[str] = field(default=None, init=False)
    """
    The owner and repository name. 
    
    For example, ``octocat/Hello-World``.
    """

    GITHUB_REPOSITORY_OWNER: Optional[str] = field(default=None, init=False)
    """
    The repository owner's name. 
    
    For example, ``octocat``.
    """

    GITHUB_RETENTION_DAYS: Optional[str] = field(default=None, init=False)
    """
    The number of days that workflow run logs and artifacts are kept. 
    
    For example, ``90``.
    """

    GITHUB_RUN_ATTEMPT: Optional[str] = field(default=None, init=False)
    """
    A unique number for each attempt of a particular workflow run in a repository. 
    
    This number begins at ``1`` for the workflow run's first attempt, and increments with each re-run.
    
    For example, ``3``.
    """

    GITHUB_RUN_ID: Optional[str] = field(default=None, init=False)
    """
    A unique number for each workflow run within a repository. 
    
    This number does not change if you re-run the workflow run. 
    
    For example, ``1658821493``.
    """

    GITHUB_RUN_NUMBER: Optional[str] = field(default=None, init=False)
    """
    A unique number for each run of a particular workflow in a repository. 
    
    This number begins at ``1`` for the workflow's first run, and increments with each new run. 
    This number does not change if you re-run the workflow run.

    For example, ``3``.
    """

    GITHUB_SERVER_URL: Optional[Union[furl, str]] = field(default=None, init=False)
    """
    The URL of the GitHub Enterprise Cloud server. 
    
    For example: ``https://github.com``.
    """

    GITHUB_SHA: Optional[str] = field(default=None, init=False)
    """
    The commit SHA that triggered the workflow. 
    
    The value of this commit SHA depends on the event that triggered the workflow.
    For more information, see `Events that trigger workflows. 
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/events-that-trigger-workflows>`_ 

    For example, ``ffac537e6cbbf934b08745a378932722df287a53``.
    """

    GITHUB_WORKFLOW: Optional[Union[Path, str]] = field(default=None, init=False)
    """
    The name of the workflow. 
    
    For example, ``My test workflow``. 
    
    If the workflow file doesn't specify a name, 
    the value of this variable is the full path of the workflow file in the repository.
    """

    GITHUB_WORKSPACE: Optional[Union[Path, str]] = field(default=None, init=False)
    """
    The default working directory on the runner for steps, and the default location of your repository 
    when using the `checkout <https://github.com/actions/checkout>`_ action. 
    
    For example, ``/home/runner/work/my-repo-name/my-repo-name``.
    """

    RUNNER_ARCH: Optional[str] = field(default=None, init=False)
    """
    The architecture of the runner executing the job. 
    
    Possible values are ``X86``, ``X64``, ``ARM``, or ``ARM64``.
    
    For example, ``X86``.
    """

    RUNNER_NAME: Optional[str] = field(default=None, init=False)
    """
    The name of the runner executing the job. 
    
    For example, ``Hosted Agent``.
    """

    RUNNER_OS: Optional[str] = field(default=None, init=False)
    """
    The operating system of the runner executing the job. 
    
    Possible values are ``Linux``, ``Windows``, or ``macOS``. 
    
    For example, ``Linux``.
    """

    RUNNER_TEMP: Optional[Union[Path, str]] = field(default=None, init=False)
    """
    The path to a temporary directory on the runner. 
    
    This directory is emptied at the beginning and end of each job. 
    
    Note that files will not be removed if the runner's user account does not have permission to delete them. 
    
    For example, ``_temp``.
    """

    RUNNER_TOOL_CACHE: Optional[str] = field(default=None, init=False)
    """
    The path to the directory containing preinstalled tools for GitHub-hosted runners. 
    
    For more information, see `About GitHub-hosted runners. 
    <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/specifications-for-github-hosted-runners/#supported-software>`_
    
    `Ubuntu latest <https://github.com/actions/virtual-environments/blob/main/images/linux/Ubuntu2004-Readme.md>`_ 
    `macOS latest <https://github.com/actions/virtual-environments/blob/main/images/macos/macos-11-Readme.md>`_

    For example, ``C:\hostedtoolcache\windows``.
    """


@dataclass
class EnvConfig(EnvBase):
    """User Set Applications Configuration Environment Variables ``/etc/profile.d/config.sh`` Class"""
    ALPINE: Optional[bool] = field(default=None, init=False)
    BASH_ENV: Optional[Path] = field(default=None, init=False)
    EDITOR: Optional[Path] = field(default=None, init=False)
    ENV: Optional[Path] = field(default=None, init=False)
    VISUAL: Optional[Path] = field(default=None, init=False)


@dataclass
class EnvDynamic(EnvBase):
    """Dynamic Environment Variables Class"""
    IPYTHONENABLE: Optional[bool] = field(default=None, init=False)
    PYCHARM_DISPLAY_PORT: Optional[int] = field(default=None, init=False)
    PYCHARM_HOSTED: Optional[str] = field(default=None, init=False)
    PYCHARM_MATPLOTLIB_INDEX: Optional[str] = field(default=None, init=False)
    PYCHARM_MATPLOTLIB_INTERACTIVE: Optional[str] = field(default=None, init=False)
    PYDEVD_LOAD_VALUES_ASYNC: Optional[str] = field(default=None, init=False)
    __INTELLIJ_COMMAND_HISTFILE__: Optional[Path] = field(default=None, init=False)


@dataclass
class EnvJetBrains(EnvBase):
    """User Set JeBrains Environment Variables ``/etc/profile.d/jetbrains.sh`` Class"""
    JETBRAINS: Optional[Path] = field(default=None, init=False)
    PYCHARM_PROPERTIES: Optional[Path] = field(default=None, init=False)
    PYCHARM_VM_OPTIONS: Optional[Path] = field(default=None, init=False)


@dataclass
class EnvPython(EnvBase):
    """User Set JeBrains Environment Variables Class"""
    PYTHONIOENCODING: Optional[str] = field(default=None, init=False)
    PYTHONUNBUFFERED: Optional[str] = field(default=None, init=False)
    PYTHONPATH: Optional[str] = field(default=None, init=False)


@dataclass
class EnvSecrets(EnvBase):
    """User Secrets Environment Variables ``/etc/profile.d/secrets.sh`` Class"""
    GH_TOKEN: Optional[str] = field(default=None, init=False)
    GITHUB_TOKEN: Optional[str] = field(default=None, init=False)


@dataclass
class EnvSystem(EnvBase):
    """System Environment Variables ``/etc/profile.d/system.sh`` Class"""
    ALPINE: Optional[bool] = field(default=None, init=False)


@dataclass
class EnvUnix(EnvBase):
    """Default/Common Linux/Unix Environment Variables Class"""
    COMMAND_MODE: Optional[str] = field(default=None, init=False)
    HOME: Optional[Path] = field(default=None, init=False)
    LC_TYPE: Optional[str] = field(default=None, init=False)
    LOGIN_SHELL: Optional[bool] = field(default=None, init=False)
    LOGNAME: Optional[str] = field(default=None, init=False)
    OLDPWD: Optional[Path] = field(default=None, init=False)
    PATH: Optional[str] = field(default=None, init=False)
    PS1: Optional[str] = field(default=None, init=False)
    PS2: Optional[str] = field(default=None, init=False)
    PS4: Optional[str] = field(default=None, init=False)
    PWD: Optional[Path] = field(default=None, init=False)
    SHELL: Optional[Path] = field(default=None, init=False)
    SHLVL: Optional[Path] = field(default=None, init=False)
    SSH_AUTH_SOCK: Optional[Path] = field(default=None, init=False)
    SUDO_GID: Optional[int] = field(default=None, init=False)
    SUDO_UID: Optional[int] = field(default=None, init=False)
    SUDO_USER: Optional[str] = field(default=None, init=False)
    TERM: Optional[str] = field(default=None, init=False)
    TERM_SESSION_ID: Optional[str] = field(default=None, init=False)
    TERMINAL_EMULATOR: Optional[str] = field(default=None, init=False)
    XPC_FLAGS: Optional[str] = field(default=None, init=False)
    XPC_SERVICE_NAME: Optional[str] = field(default=None, init=False)
    USER: Optional[str] = field(default=None, init=False)
    TMPDIR: Optional[Path] = field(default=None, init=False)
    _: Optional[Path] = field(default=None, init=False)
    __CF_USER_TEXT_ENCODING: Optional[str] = field(default=None, init=False)
    __CFBundleIdentifier: Optional[str] = field(default=None, init=False)


@dataclass
class Env(EnvAction, EnvConfig, EnvDynamic, EnvJetBrains, EnvPython, EnvSecrets, EnvSystem, EnvUnix):
    """Environment Class"""


def parse_env(name: str = 'USER') -> Optional[Union[bool, Path, furl, int, IPAddressType, str]]:
    """
    Parses variable from environment using :func:`mreleaser.parse_str`,
    except ``SUDO_UID`` or ``SUDO_GID`` which are parsed as int instead of bool.

    Arguments:
        name: variable name to parse from environment (default: USER)

    Examples:
        >>> isinstance(parse_env(), str)
        True

        >>> os.environ['FOO'] = '1'
        >>> parse_env('FOO')
        True
        >>> os.environ['FOO'] = '0'
        >>> parse_env('FOO')
        False
        >>> os.environ['FOO'] = 'TrUe'
        >>> parse_env('FOO')
        True
        >>> os.environ['FOO'] = 'OFF'
        >>> parse_env('FOO')
        False

        >>> os.environ['FOO'] = '~/foo'
        >>> parse_env('FOO') == Path('~/foo')
        True
        >>> os.environ['FOO'] = '/foo'
        >>> parse_env('FOO') == Path('/foo')
        True
        >>> os.environ['FOO'] = './foo'
        >>> parse_env('FOO') == Path('./foo')
        True
        >>> os.environ['FOO'] = './foo'
        >>> parse_env('FOO') == Path('./foo')
        True

        >>> os.environ['FOO'] = 'https://github.com'
        >>> parse_env('FOO').url
        'https://github.com'
        >>> os.environ['FOO'] = 'git@github.com'
        >>> parse_env('FOO').url
        'git@github.com'

        >>> os.environ['FOO'] = '0.0.0.0'
        >>> parse_env('FOO').exploded
        '0.0.0.0'
        >>> os.environ['FOO'] = '::1'
        >>> parse_env('FOO').exploded
        '0000:0000:0000:0000:0000:0000:0000:0001'

        >>> os.environ['FOO'] = '3'
        >>> parse_env('FOO')
        3

        >>> os.environ['FOO'] = '2.0'
        >>> parse_env('FOO')
        '2.0'
        >>> parse_env('PATH') == os.environ['PATH']
        True

        >>> del os.environ['FOO']
        >>> parse_env('FOO')

    Returns:
        Parsed result or None
    """
    if value := os.environ.get(name):
        return EnvBase.as_int(name, value)
    return value


def parse_str(data: Any = None) -> Optional[Union[bool, Path, furl, int, IPAddressType, str]]:
    """
    Parses str or data.__str__()

    Parses:
        - bool: 1, 0, True, False, yes, no, on, off (case insensitive)
        - int: integer only numeric characters but 1 and 0
        - ipaddress: ipv4/ipv6 address
        - url: if "://" or "@" is found it will be parsed as url
        - path: if "." or start with "/" or "~" or "." and does contain ":"
        - others as string

    Arguments:
        data: variable name to parse from environment (default: USER)

    Examples:
        >>> parse_str()

        >>> parse_str('1')
        True
        >>> parse_str('0')
        False
        >>> parse_str('TrUe')
        True
        >>> parse_str('OFF')
        False

        >>> parse_str('https://github.com').url
        'https://github.com'
        >>> parse_str('git@github.com').url
        'git@github.com'

        >>> parse_str('~/foo') == Path('~/foo')
        True
        >>> parse_str('/foo') == Path('/foo')
        True
        >>> parse_str('./foo') == Path('./foo')
        True
        >>> parse_str('.') == Path('.')
        True
        >>> parse_str(Path()) == Path()
        True
        >>> parse_str(Path('/foo')) == Path('/foo')
        True

        >>> parse_str('0.0.0.0').exploded
        '0.0.0.0'
        >>> parse_str('::1').exploded
        '0000:0000:0000:0000:0000:0000:0000:0001'

        >>> parse_str('2')
        2

        >>> parse_str('2.0')
        '2.0'
        >>> parse_str('/usr/share/man:')
        '/usr/share/man:'
        >>> parse_str(os.environ['PATH']) == os.environ['PATH']
        True

    Returns:
        None
    """
    if data is not None:
        if not isinstance(data, str): data = str(data)

        if data.lower() in ['1', 'true', 'yes', 'on']:
            return True
        elif data.lower() in ['0', 'false', 'no', 'off']:
            return False
        elif '://' in data or '@' in data:
            return furl(data)
        elif data[0] in ['/', '~', '.'] and ':' not in data:
            return Path(data)
        else:
            try:
                return ipaddress.ip_address(data)
            except ValueError:
                if data.isnumeric():
                    return int(data)
    return data


def version(package: str = app.info.name) -> str:
    """
    Package installed version

    Examples:
        >>> len(version('pip').split('.'))  # doctest: +ELLIPSIS
        3

    Arguments:
        package: package name (Default: `PROJECT`)

    Returns
        Installed version
    """
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        pass


@app.command(name='package')
def _package(path: Optional[list[Path]] = Argument('.', help='Directory Path to package'),) -> None:
    """
    Prints the package name from setup.cfg in path.

    \b


    Returns:
        None
    """
    print(version())


@app.command(name='--version')
def _version() -> None:
    """
    Prints the installed version of the package.

    Returns:
        None
    """
    print(version())


if __name__ == "__main__":
    from typer import Exit
    try:
        Exit(app())
    except KeyboardInterrupt:
        print('Aborted!')
        Exit()
