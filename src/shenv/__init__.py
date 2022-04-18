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

    'Cli',

    'EnvBase',
    'EnvAction',
    'EnvConfig',
    'EnvDynamic',
    'EnvGit',
    'EnvGlobal',
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
from typing import Callable
from typing import IO
from typing import Optional
from typing import Type
from typing import Union



try:
    from ppath import Path
except ImportError:
    from pathlib import Path

import click
import typer
import typer.testing
from furl import furl
from typer import Argument
from typer.models import Default

ENV_PARSE_AS_INT_NAME = ('GIT_MERGE_VERBOSITY', 'PID', 'PPID',)
ENV_PARSE_AS_INT_SUFFIX = ('_ATTEMPT', '_ID', '_GID', '_JOBS', '_NUMBER', '_PORT', '_UID',)

LINUX = sys.platform == "linux"
MACOS = sys.platform == "darwin"
HELP_OPTIONS = dict(help_option_names=['-h', '--help'])

AnyPath = Union[Path, PathLike, AnyStr, IO[AnyStr]]
ExcType = Union[Type[Exception], tuple[Type[Exception], ...]]
IPAddressType = Union[IPv4Address, IPv6Address]

cli_invoke = typer.testing.CliRunner().invoke


class Cli(typer.Typer):
    """Wrapper for :class:`typer.Typer`"""

    help_option_names = ['-h', '--help']
    context_settings_default = dict(help_option_names=help_option_names)

    def __init__(self, *, name: Optional[str] = Default(None), cls: Optional[Type[click.Command]] = Default(None),
                 invoke_without_command: bool = Default(False), no_args_is_help: bool = Default(False),
                 subcommand_metavar: Optional[str] = Default(None), chain: bool = Default(False),
                 result_callback: Optional[Callable[..., Any]] = Default(None),
                 # Command
                 context_settings: Optional[dict[Any, Any]] = Default(None),
                 callback: Optional[Callable[..., Any]] = Default(None),
                 help_: Optional[str] = Default(None), epilog: Optional[str] = Default(None),
                 short_help: Optional[str] = Default(None), options_metavar: str = Default("[OPTIONS]"),
                 add_help_option: bool = Default(True), hidden: bool = Default(False),
                 deprecated: bool = Default(False), add_completion: bool = False, ):
        """
        Typer Instance with defaults changed.

        Args:
            name: application name
            cls: click.Command class
            invoke_without_command: invoke_without_command
            no_args_is_help: no_args_is_help
            subcommand_metavar: subcommand_metavar
            chain: chain
            result_callback: result_callback
            context_settings: context_settings
            callback: callback
            help_: help
            epilog: epilog
            short_help: short_help
            options_metavar: options_metavar
            add_help_option: add_help_option
            hidden: hidden
            deprecated: deprecated
            add_completion: add_completion
        """
        context_settings.update(self.context_settings_default)
        super().__init__(name=name, cls=cls, invoke_without_command=invoke_without_command,
                         no_args_is_help=no_args_is_help, subcommand_metavar=subcommand_metavar, chain=chain,
                         result_callback=result_callback, context_settings=context_settings, callback=callback,
                         help=help_, epilog=epilog, short_help=short_help, options_metavar=options_metavar,
                         add_help_option=add_help_option, hidden=hidden, deprecated=deprecated,
                         add_completion=add_completion)

    def run(self) -> None:
        """
        Helper function to run the application in __main__:

        if __name__ == "__main__"::
            from typer import Exit
            try:
                Exit(app())
            except KeyboardInterrupt:
                print('Aborted!')
                Exit()
        Returns:
            None
        """
        try:
            typer.Exit(self())
        except KeyboardInterrupt:
            typer.secho('Aborted!', fg=typer.colors.RED, bold=True)
            typer.Exit()


cli = Cli()


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
        <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflow-commands-for-github-actions
        /#setting-an-environment-variable>`_.

    If you want to pass a value from a step in one job in a ``workflow`` to a step in another job in the workflow,
        you can define the value as a job output, see `Syntax
        <https://docs.github.com/en/enterprise-cloud@latest/actions/learn-github-actions/workflow-syntax-for-github
        -actions#jobsjob_idoutputs>`_.
    """
    CI: Optional[Union[bool, str]] = field(default=None, init=False)
    """
    Always set to ``true`` in a GitHub Actions environment.
    """
    GITHUB_ACTION: Optional[str] = field(default=None, init=False)
    """
    The name of the action currently running, or the step `id
<https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-syntax-for-github-actions
#jobsjob_idstepsid>`_.
    
    For example, for an action, ``__repo-owner_name-of-action-repo``.
    
    GitHub removes special characters, and uses the name ``__run`` when the current step runs a script without an id. 

    If you use the same script or action more than once in the same job, 
    the name will include a suffix that consists of the sequence number preceded by an underscore. 
    
    For example, the first script you run will have the name ``__run``, and the second script will be named 
    ``__run_2``. 

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
    <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-commands-for-github-actions
    #setting-an-environment-variable>`_
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
    <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/workflow-syntax-for-github-actions
    #jobsjob_id>`_ 
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
     <https://docs.github.com/en/enterprise-cloud@latest/actions/using-workflows/workflow-commands-for-github-actions
     #adding-a-system-path>`_
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
    <https://docs.github.com/en/enterprise-cloud@latest/actions/reference/specifications-for-github-hosted-runners
    /#supported-software>`_
    
    `Ubuntu latest <https://github.com/actions/virtual-environments/blob/main/images/linux/Ubuntu2004-Readme.md>`_ 
    `macOS latest <https://github.com/actions/virtual-environments/blob/main/images/macos/macos-11-Readme.md>`_

    For example, ``C:\hostedtoolcache\windows``.
    """


@dataclass
class EnvConfig(EnvBase):
    """User Set Applications Configuration Environment Variables ``/etc/profile.d/config.sh`` Class"""
    BASH_ENV: Optional[Path] = field(default=None, init=False)
    DIRENV_CONFIG: Optional[Path] = field(default=None, init=False)
    EDITOR: Optional[Path] = field(default=None, init=False)
    EMAIL: Optional[furl] = field(default=None, init=False)
    """
    is the Git fallback email address in case the user.email configuration value isn’t set. 
    If this isn’t set, Git falls back to the system user and host names.
    """
    ENV: Optional[Path] = field(default=None, init=False)
    PAGER: Optional[str] = field(default=None, init=False)
    PREFIX: Optional[Path] = field(default=None, init=False)
    """
    like HOME but for the Git system-wide configuration. Git looks for this file at $PREFIX/etc/gitconfig.
    """
    STOW_DIR: Optional[Path] = field(default=None, init=False)
    """
    See Also: `Stow <https://www.gnu.org/software/stow/manual/stow.html>`_
    """
    VISUAL: Optional[str] = field(default=None, init=False)


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
class EnvGit(EnvBase):
    """
    User Set Git Configuration Environment Variables ``/etc/profile.d/config.sh`` Class

    `Git Internals Environment Variables <https://git-scm.com/book/en/v2/Git-Internals-Environment-Variables>`_

    Types:

        - Global Behavior: Some of Git’s general behavior as a computer program depends on environment variables.
        - Repository Locations: Git uses several environment variables to determine
                                how it interfaces with the current repository.
        - Pathspecs: Refers to how you specify paths to things in Git, including the use of wildcards.
                     These are used in the .gitignore file, but also on the command-line (git add *.c).
        - Committing: The final creation of a Git commit object is usually done by git-commit-tree,
                      which uses these environment variables as its primary source of information,
                      falling back to configuration values only if these aren’t present.
        - Networking: Git uses the curl library to do network operations over HTTP,
                      so GIT_CURL_VERBOSE tells Git to emit all the messages generated by that library.
                      This is similar to doing curl -v on the command line.
        - Diffing and Merging.
        - Debugging: Want to really know what Git is up to? Git has a fairly complete set of traces embedded,
                     and all you need to do is turn them on.
                     The possible values of these variables are as follows:

                     - “true”, “1”, or “2” – the trace category is written to stderr.
                     - An absolute path starting with / – the trace output will be written to that file.
        - Miscellaneous.
        - Configuration: Get and set repository or global options `Git Config <https://git-scm.com/docs/git-config>`_

    See Also:

        - `Getting Started <https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control>`_
        - `Git Tools Credential Storage <https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage>`_
        - `Git Credential Manager <https://github.com/GitCredentialManager/git-credential-manager>`_

    """
    # Global Behavior
    GIT_EXEC_PATH: Optional[Path] = field(default=None, init=False)
    """
    """
    GIT_CONFIG_NOSYSTEM: Optional[bool] = field(default=None, init=False)
    """
    if set, disables the use of the system-wide configuration file. 
    This is useful if your system config is interfering with your commands, 
    but you don’t have access to change or remove it
    """
    GIT_PAGER: Optional[str] = field(default=None, init=False)
    """
    controls the program used to display multi-page output on the command line. 
    If this is unset, PAGER will be used as a fallback
    """
    GIT_EDITOR: Optional[str] = field(default=None, init=False)
    """
    is the editor Git will launch when the user needs to edit some text (a commit message, for example). 
    If unset, EDITOR will be used
    """
    # Repository Locations
    GIT_DIR: Optional[Path] = field(default=None, init=False)
    """
    is the location of the .git folder. If this isn’t specified, 
    Git walks up the directory tree until it gets to ~ or /, looking for a .git directory at every step
    """
    GIT_CEILING_DIRECTORIES: Optional[str] = field(default=None, init=False)
    """
    controls the behavior of searching for a .git directory. 
    If you access directories that are slow to load 
    (such as those on a tape drive, or across a slow network connection), 
    you may want to have Git stop trying earlier than it might otherwise, 
    especially if Git is invoked when building your shell prompt.
    """
    GIT_WORK_TREE: Optional[str] = field(default=None, init=False)
    """
    is the location of the root of the working directory for a non-bare repository. 
    If --git-dir or GIT_DIR is specified but none of --work-tree, GIT_WORK_TREE or core.worktree is specified, 
    the current working directory is regarded as the top level of your working tree.
    """
    GIT_INDEX_FILE: Optional[str] = field(default=None, init=False)
    """
    is the path to the index file (non-bare repositories only).
    """
    GIT_OBJECT_DIRECTORY: Optional[str] = field(default=None, init=False)
    """
    can be used to specify the location of the directory that usually resides at .git/objects.
    """
    GIT_ALTERNATE_OBJECT_DIRECTORIES: Optional[str] = field(default=None, init=False)
    """
    is a colon-separated list (formatted like /dir/one:/dir/two:…) 
    which tells Git where to check for objects if they aren’t in GIT_OBJECT_DIRECTORY. 
    If you happen to have a lot of projects with large files that have the exact same contents, 
    this can be used to avoid storing too many copies of them.
    """
    # Pathspecs
    GIT_GLOB_PATHSPECS: Optional[str] = field(default=None, init=False)
    """
    if set to 1, wildcard characters act as wildcards (which is the default)
    """
    GIT_NOGLOB_PATHSPECS: Optional[str] = field(default=None, init=False)
    """
    if set to 1, wildcard characters only match themselves, 
    meaning something like *.c would only match a file named “\*.c”, rather than any file whose name ends with .c. 
    You can override this in individual cases by starting the pathspec with :(glob) or :(literal), as in :(glob)\*.c.
    """
    GIT_LITERAL_PATHSPECS: Optional[str] = field(default=None, init=False)
    """
    disables both of the above behaviors; no wildcard characters will work, 
    and the override prefixes are disabled as well.
    """
    GIT_ICASE_PATHSPECS: Optional[str] = field(default=None, init=False)
    """
    sets all pathspecs to work in a case-insensitive manner.
    """
    # Committing
    GIT_AUTHOR_NAME: Optional[str] = field(default=None, init=False)
    """
    is the human-readable name in the “author” field.
    """
    GIT_AUTHOR_EMAIL: Optional[furl] = field(default=None, init=False)
    """
    is the email for the “author” field.
    """
    GIT_AUTHOR_DATE: Optional[str] = field(default=None, init=False)
    """
    is the timestamp used for the “author” field.
    """
    GIT_COMMITTER_NAME: Optional[str] = field(default=None, init=False)
    """
    sets the human name for the “committer” field..
    """
    GIT_COMMITTER_EMAIL: Optional[furl] = field(default=None, init=False)
    """
    is the email address for the “committer” field.
    """
    GIT_COMMITTER_DATE: Optional[str] = field(default=None, init=False)
    """
    is used for the timestamp in the “committer” field.
    """
    # Networking
    GIT_SSL_NO_VERIFY: Optional[bool] = field(default=None, init=False)
    """
    tells Git not to verify SSL certificates. 
    This can sometimes be necessary if you’re using a self-signed certificate to serve Git repositories over HTTPS,
    or you’re in the middle of setting up a Git server but haven’t installed a full certificate yet.
    """
    GIT_HTTP_LOW_SPEED_LIMIT: Optional[str] = field(default=None, init=False)
    """
    if the data rate of an HTTP operation is lower than GIT_HTTP_LOW_SPEED_LIMIT bytes per second for longer 
    than GIT_HTTP_LOW_SPEED_TIME seconds, Git will abort that operation. 
    These values override the http.lowSpeedLimit and http.lowSpeedTime configuration values.
    """
    GIT_HTTP_LOW_SPEED_TIME: Optional[str] = field(default=None, init=False)
    """
    if the data rate of an HTTP operation is lower than GIT_HTTP_LOW_SPEED_LIMIT bytes per second for longer 
    than GIT_HTTP_LOW_SPEED_TIME seconds, Git will abort that operation. 
    These values override the http.lowSpeedLimit and http.lowSpeedTime configuration values.
    """
    GIT_HTTP_USER_AGENT: Optional[str] = field(default=None, init=False)
    """
    sets the user-agent string used by Git when communicating over HTTP. The default is a value like git/2.0.0.
    """
    # Diffing and Merging
    GIT_DIFF_OPTS: Optional[str] = field(default=None, init=False)
    """
    is a bit of a misnomer. The only valid values are -u<n> or --unified=<n>, 
    which controls the number of context lines shown in a git diff command.
    """
    GIT_EXTERNAL_DIFF: Optional[str] = field(default=None, init=False)
    """
    is used as an override for the diff.external configuration value. 
    If it’s set, Git will invoke this program when git diff is invoked.
    """
    GIT_DIFF_PATH_COUNTER: Optional[str] = field(default=None, init=False)
    """
    GIT_DIFF_PATH_COUNTER and GIT_DIFF_PATH_TOTAL are useful from inside the program specified by GIT_EXTERNAL_DIFF 
    or diff.external. The former represents which file in a series is being diffed (starting with 1), 
    and the latter is the total number of files in the batch.
    """
    GIT_DIFF_PATH_TOTAL: Optional[str] = field(default=None, init=False)
    """
    GIT_DIFF_PATH_COUNTER and GIT_DIFF_PATH_TOTAL are useful from inside the program specified by GIT_EXTERNAL_DIFF 
    or diff.external. The former represents which file in a series is being diffed (starting with 1), 
    and the latter is the total number of files in the batch.
    """
    GIT_MERGE_VERBOSITY: Optional[int] = field(default=None, init=False)
    """
    controls the output for the recursive merge strategy. The allowed values are as follows (The default value is 2):

        - 0 outputs nothing, except possibly a single error message.
        - 1 shows only conflicts.
        - 2 also shows file changes.
        - 3 shows when files are skipped because they haven’t changed.
        - 4 shows all paths as they are processed.
        - 5 and above show detailed debugging information.
    """
    # Debugging
    GIT_TRACE: Optional[bool] = field(default=None, init=False)
    """
    controls general traces, which don’t fit into any specific category. 
    This includes the expansion of aliases, and delegation to other sub-programs.
    
    For example: GIT_TRACE=true git lga
    """
    GIT_TRACE_PACK_ACCESS: Optional[bool] = field(default=None, init=False)
    """
    controls tracing of packfile access. The first field is the packfile being accessed, 
    the second is the offset within that file:
    
    For example: GIT_TRACE_PACK_ACCESS=true git status
    """
    GIT_TRACE_PACKET: Optional[bool] = field(default=None, init=False)
    """
    enables packet-level tracing for network operations.
    
    For example: GIT_TRACE_PACKET=true git ls-remote origin
    """
    GIT_TRACE_PERFORMANCE: Optional[bool] = field(default=None, init=False)
    """
    controls logging of performance data. The output shows how long each particular git invocation takes
    
    For example: GIT_TRACE_PERFORMANCE=true git gc
    """
    GIT_TRACE_SETUP: Optional[bool] = field(default=None, init=False)
    """
    shows information about what Git is discovering about the repository and environment it’s interacting with.
    
    For example: GIT_TRACE_SETUP=true git status
    """
    # Miscellaneous
    GIT_SSH: Optional[str] = field(default=None, init=False)
    """
    if specified, is a program that is invoked instead of ssh when Git tries to connect to an SSH host. 
    It is invoked like $GIT_SSH [username@]host [-p <port>] <command>. 
    Note that this isn’t the easiest way to customize how ssh is invoked; 
    it won’t support extra command-line parameters, 
    so you’d have to write a wrapper script and set GIT_SSH to point to it. 
    It’s probably easier just to use the ~/.ssh/config file for that.
    """
    GIT_ASKPASS: Optional[str] = field(default=None, init=False)
    """
    is an override for the core.askpass configuration value. This is the program invoked whenever 
    Git needs to ask the user for credentials, which can expect a text prompt as a command-line argument, 
    and should return the answer on stdout (see `Credential Storage 
    <https://git-scm.com/book/en/v2/ch00/_credential_caching>`_ for more on this subsystem).
    """
    GIT_NAMESPACE: Optional[str] = field(default=None, init=False)
    """
    controls access to namespaced refs, and is equivalent to the --namespace flag. 
    This is mostly useful on the server side, 
    where you may want to store multiple forks of a single repository in one repository, only keeping the refs separate.
    """
    GIT_FLUSH: Optional[bool] = field(default=None, init=False)
    """
    can be used to force Git to use non-buffered I/O when writing incrementally to stdout. 
    A value of 1 causes Git to flush more often, a value of 0 causes all output to be buffered. 
    The default value (if this variable is not set) is to choose an appropriate buffering scheme 
    depending on the activity and the output mode.
    """
    GIT_REFLOG_ACTION: Optional[str] = field(default=None, init=False)
    """
    lets you specify the descriptive text written to the reflog. 
    
    For example:
    GIT_REFLOG_ACTION="my action" git commit --allow-empty -m 'My message'
    git reflog -1
    """
    # Configuration
    GIT_CONFIG_GLOBAL: Optional[Path] = field(default=None, init=False)
    """
    Take the configuration from the given files instead from global $HOME configuration. 
    See git[1] for details.
    """
    GIT_CONFIG_SYSTEM: Optional[Path] = field(default=None, init=False)
    """
    Take the configuration from the given files instead from system $PREFIX configuration. 
    See git[1] for details.
    """
    GIT_CONFIG_COUNT: Optional[int] = field(default=None, init=False)
    """
    If GIT_CONFIG_COUNT is set to a positive number, 
    all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> 
    up to that number will be added to the process’s runtime configuration. 
    The config pairs are zero-indexed. Any missing key or value is treated as an error. 
    An empty GIT_CONFIG_COUNT is treated the same as GIT_CONFIG_COUNT=0, namely no pairs are processed. 
    These environment variables will override values in configuration files, 
    but will be overridden by any explicit options passed via git -c.

    This is useful for cases where you want to spawn multiple git commands with a common configuration 
    but cannot depend on a configuration file, for example when writing scripts.
    """
    GIT_CONFIG_KEY_1: Optional[str] = field(default=None, init=False)
    """
    """
    GIT_CONFIG_VALUE_1: Optional[str] = field(default=None, init=False)
    """
    """
    GIT_CONFIG_KEY_2: Optional[str] = field(default=None, init=False)
    """
    """
    GIT_CONFIG_VALUE_2: Optional[str] = field(default=None, init=False)
    """
    """
    GIT_CONFIG: Optional[str] = field(default=None, init=False)
    """
    If no --file option is provided to git config, use the file given by GIT_CONFIG as if it were provided via --file. 
    This variable has no effect on other Git commands, and is mostly for historical compatibility; 
    there is generally no reason to use it instead of the --file option.
    """
    GIT_TEMPLATE_DIR: Optional[str] = field(default=None, init=False)
    """
    Files and directories in the template directory whose name do not start with a dot 
    will be copied to the $GIT_DIR after it is created.
    
    The template directory will be one of the following (in order):

        - the argument given with the --template option;

        - the contents of the $GIT_TEMPLATE_DIR environment variable;

        - the init.templateDir configuration variable; or

        - the default template directory: /usr/share/git-core/templates.

    The default template directory includes some directory structure, 
          suggested "exclude patterns" (see gitignore[5]), and sample hook files.

    The sample hooks are all disabled by default. 
    To enable one of the sample hooks rename it by removing its .sample suffix.

    See githooks[5] for more general info on hook execution.
    """


@dataclass
class EnvGlobal(EnvBase):
    """User Set Global Configuration Environment Variables ``/etc/profile.d/global.sh`` Class"""
    BASH_ENV: Optional[Path] = field(default=None, init=False)
    EDITOR: Optional[Path] = field(default=None, init=False)
    EMAIL: Optional[furl] = field(default=None, init=False)
    """
    is the Git fallback email address in case the user.email configuration value isn’t set. 
    If this isn’t set, Git falls back to the system user and host names.
    """
    ENV: Optional[Path] = field(default=None, init=False)
    PAGER: Optional[str] = field(default=None, init=False)
    PREFIX: Optional[Path] = field(default=None, init=False)
    """
    like HOME but for the Git system-wide configuration. Git looks for this file at $PREFIX/etc/gitconfig.
    """
    VISUAL: Optional[str] = field(default=None, init=False)


@dataclass
class EnvJetBrains(EnvBase):
    """User Set JeBrains Environment Variables ``/etc/profile.d/jetbrains.sh`` Class"""
    JETBRAINS: Optional[Path] = field(default=None, init=False)
    PYCHARM_PROPERTIES: Optional[Path] = field(default=None, init=False)
    PYCHARM_VM_OPTIONS: Optional[Path] = field(default=None, init=False)


@dataclass
class EnvPython(EnvBase):
    """User Set JeBrains Environment Variables ``/etc/profile.d/config.sh``Class"""
    PYTHONBREAKPOINT: Optional[bool] = field(default=None, init=False)
    """"
    if this variable is set to 0, it disables the default
    debugger. It can be set to the callable of your debugger of choice.
    """
    PYTHONCOERCECLOCALE: Optional[bool] = field(default=None, init=False)
    """
    if this variable is set to 0, it disables the locale
    coercion behavior. Use PYTHONCOERCECLOCALE=warn to request display of
    locale coercion and locale compatibility warnings on stderr.
    """
    PYTHONDEBUG: Optional[bool] = field(default=None, init=False)
    """
    turn on parser debugging output (for experts only, only works on
    debug builds)
    """
    PYTHONDEVMODE: Optional[bool] = field(default=None, init=False)
    """"
    enable the development mode.
    """
    PYTHONDONTWRITEBYTECODE: Optional[bool] = field(default=None, init=False)
    """
    don't write .pyc files on import.
    """
    PYTHONFAULTHANDLER: Optional[bool] = field(default=None, init=False)
    """
    dump the Python traceback on fatal errors.
    """
    PYTHONHASHSEED: Optional[str] = field(default=None, init=False)
    """
    if this variable is set to 'random', a random value is used
    to seed the hashes of str and bytes objects.  It can also be set to an
    integer in the range [0,4294967295] to get hash values with a
    predictable seed.
    """
    PYTHONHOME: Optional[str] = field(default=None, init=False)
    """
    alternate <prefix> directory (or <prefix>:<exec_prefix>).
    The default module search path uses <prefix>/lib/pythonX.X.
    """
    PYTHONINSPECT: Optional[bool] = field(default=None, init=False)
    """
    inspect interactively after running script; forces a prompt even
    if stdin does not appear to be a terminal.
    """
    PYTHONIOENCODING: Optional[bool] = field(default=None, init=False)
    """
    Encoding[:errors] used for stdin/stdout/stderr.
    """
    PYTHONMALLOC: Optional[str] = field(default=None, init=False)
    """
    set the Python memory allocators and/or install debug hooks on Python memory allocators. 
    Use PYTHONMALLOC=debug to install debug hooks.
    """
    PYTHONNOUSERSITE: Optional[bool] = field(default=None, init=False)
    """
    don't add user site directory to sys.path.
    """
    PYTHONOPTIMIZE: Optional[bool] = field(default=None, init=False)
    """
    remove assert and __debug__-dependent statements; add .opt-1 before
    .pyc extension
    """
    PYTHONPATH: Optional[str] = field(default=None, init=False)
    """':'-separated list of directories prefixed to the
               default module search path.  The result is sys.path.
"""
    PYTHONPLATLIBDIR: Optional[Path] = field(default=None, init=False)
    """
    override sys.platlibdir.
    """
    PYTHONPYCACHEPREFIX: Optional[Path] = field(default=None, init=False)
    """
    root directory for bytecode cache (pyc) files.
    """
    PYTHONSTARTUP: Optional[Path] = field(default=None, init=False)
    """
    file executed on interactive startup (no default).
    """
    PYTHONUNBUFFERED: Optional[bool] = field(default=None, init=False)
    """
    force the stdout and stderr streams to be unbuffered;
    this option has no effect on stdin.
    """
    PYTHONUTF8: Optional[bool] = field(default=None, init=False)
    """
    if set to 1, enable the UTF-8 mode.
    """
    PYTHONVERBOSE: Optional[str] = field(default=None, init=False)
    """
    verbose (trace import statements)
    can be supplied multiple times to increase verbosity.
    """
    PYTHONWARNDEFAULTENCODING: Optional[str] = field(default=None, init=False)
    """
    enable opt-in EncodingWarning for 'encoding=None'.
    """
    PYTHONWARNINGS: Optional[str] = field(default=None, init=False)
    """
    warning control; arg is action:message:category:module:lineno.
    """


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
    """
    isn’t usually considered customizable (too many other things depend on it), 
    but it’s where Git looks for the global configuration file. 
    If you want a truly portable Git installation, complete with global configuration, 
    you can override HOME in the portable Git’s shell profile.
    """
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
class Env(EnvAction, EnvConfig, EnvDynamic, EnvGit, EnvGlobal, EnvJetBrains, EnvPython, EnvSecrets, EnvSystem, EnvUnix):
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


def version(package: str = cli.info.name) -> str:
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


class Command:
    """CLI Application Commands Class"""

    @staticmethod
    @cli.command()
    def package(path: Optional[list[Path]] = Argument('.', help='Directory Path to package'), ) -> None:
        """
        Prints the package name from setup.cfg in path.

        \b


        Returns:
            None
        """
        print(version())

    @staticmethod
    @cli.command()
    def prefix(path: Optional[list[Path]] = Argument('.', help='Directory Path to package'), ) -> None:
        """
        Prints the package name from setup.cfg in path.

        \b


        Returns:
            None
        """
        print(version())

    @staticmethod
    @cli.command(name='--version')
    def version(self) -> None:
        """
        Prints the installed version of the package.

        Returns:
            None
        """
        print(version())


if __name__ == "__main__":
    cli.run()
