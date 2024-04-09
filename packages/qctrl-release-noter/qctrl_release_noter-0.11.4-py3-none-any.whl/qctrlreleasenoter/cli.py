# Copyright 2024 Q-CTRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
The CLI tool to generate release note.
"""
import click
from git import (
    InvalidGitRepositoryError,
    Repo,
)

from qctrlreleasenoter.generate_release_notes import (
    generate_note,
    pull_latest_changes,
)


@click.command(
    help="""
    Prints release notes for the commits between the latest tag and `branch`
    for the specified repository.

    Commits are expected to follow the Conventional Commits specification
    (https://www.conventionalcommits.org/en/v1.0.0/). That is, messages are
    typically expected to be of the form:

        \b
        <kind>: <title>

        \b
        <description>

    The valid types and the release type they lead to are defined in the
    contributing guidelines (https://code.q-ctrl.com/contributing).

    Messages for commits introducing breaking changes are expected to be of
    the form:

        \b
        <kind>!: <title>

        \b
        <description>

        \b
        BREAKING CHANGE: <explanation of the breaking change>
    """
)
@click.option(
    "--branch",
    default="master",
    help="Branch on which the release will be made (defaults to master).",
)
@click.option(
    "--github",
    is_flag=True,
    default=False,
    help="Open GitHub with the release notes prefilled.",
)
@click.option(
    "--phase",
    type=click.Choice(["stable", "alpha", "beta"]),
    default="stable",
    help="Select the phase for the release (defaults to stable).",
)
@click.option(
    "--pull/--no-pull",
    default=True,
    help="Pull the latest changes from remote for the specified --branch (defaults to --pull).",
)
@click.option(
    "--allow-empty",
    is_flag=True,
    default=False,
    help="Create a release notes template even if the release notes would be empty otherwise.",
)
@click.argument("path", default=".", type=click.Path(exists=True))
def main(branch, github, path, phase, allow_empty, pull):
    """
    Main entry to generate the release note.
    """
    try:
        repo = Repo(path)
    except InvalidGitRepositoryError as err:
        raise RuntimeError("The current directory is not a valid repository.") from err

    if pull:
        pull_latest_changes(branch, repo)

    generate_note(branch, github, phase, repo, allow_empty)
