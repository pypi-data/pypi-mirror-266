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
Generates release notes based on the commit history since the last release.
"""
from __future__ import annotations

import re
import webbrowser
from dataclasses import (
    dataclass,
    field,
    fields,
)
from enum import Enum
from functools import partial
from itertools import islice
from pathlib import Path
from typing import (
    Iterator,
    Optional,
)
from urllib.parse import quote_plus

import click
import pyinflect
from git.objects import Commit
from git.refs.tag import TagReference
from packaging.version import (
    VERSION_PATTERN,
    Version,
    parse,
)


class _PrType(Enum):
    MINOR = ("feat",)
    PATCH = ("fix", "perf", "revert", "build")
    IGNORED = ("refactor", "chore", "ci", "docs", "style", "test")
    # Using an empty tuple here seems to cause issue in Python 3.11.1,
    # as it's treated as an object instead of an iterable.
    # Therefore, in `_classify_commit_type` we exclude the UNKNOWN item.
    UNKNOWN = ()


def _classify_commit_type(kind: str) -> _PrType:
    """
    Classify the PR type for a commit based on its kind.
    This could be a classmethod of _PrType, but it's convenient for type-checking as
    a private function.
    """
    # Classify the types for valid PRs in the release note.
    for type_ in islice(_PrType, len(_PrType) - 1):
        if kind in type_.value:
            return type_
    # Label the invalid PR.
    return _PrType.UNKNOWN


@dataclass
class _CommitInfo:
    title: str
    kind: _PrType
    sha: Optional[str]
    breaking_change_message: Optional[str]


class _ReleasePhase(Enum):
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"


@dataclass
class NoteBody:
    """
    Dataclass to hold the body of release note.
    """

    major: list[str] = field(default_factory=list)
    minor: list[str] = field(default_factory=list)
    patch: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        """
        Check whether the note body is empty.
        """
        return (
            sum(
                map(
                    len, (getattr(self, field.name) for field in fields(self.__class__))
                )
            )
            == 0
        )

    def add_item(self, item: _CommitInfo) -> None:
        """
        Update note body from a commit item.
        """
        # Handle the breaking change first since
        # any valid PR could be a breaking one.
        if item.breaking_change_message is not None:
            self.major.append(item.breaking_change_message)

        if item.kind is _PrType.IGNORED:
            return
        if item.kind is _PrType.UNKNOWN:
            print_warning(
                f"Commit {item.sha} has unknown kind {item.kind!r}, "
                "appending to unknown changes."
            )
            self.unknown.append(convert_to_past_tense(item.title))
        else:
            pr_type = getattr(self, item.kind.name.lower())
            pr_type.append(convert_to_past_tense(item.title))


def pull_latest_changes(branch, repo):
    """
    Pulls the latest changes from remote for the specified `branch`.
    """
    repo.git.checkout(branch)
    repo.remotes.origin.pull()


def is_version(tag: TagReference) -> bool:
    """
    Use packaging.version's regex to determine if a tag name is a valid version.
    See also: https://packaging.pypa.io/en/stable/version.html
    """
    return (
        re.match(VERSION_PATTERN, tag.name, flags=re.VERBOSE | re.IGNORECASE)
        is not None
    )


def generate_note(branch, github, phase, repo, allow_empty):
    """
    Generate release notes for the commits between the latest tag and `branch`.
    """

    # Filter to tags that look like versions, and then find the most recent.
    tags = filter(is_version, repo.tags)
    latest_tag = max(tags, key=lambda tag: tag.commit.committed_date, default=None)
    if latest_tag is not None:
        latest_tag_name = latest_tag.name
        commits = repo.iter_commits(f"{latest_tag_name}..{branch}", reverse=True)
    else:
        # Meaning this is the first release of the target repo.
        latest_tag_name = None
        commits = repo.iter_commits(reverse=True)

    note_body = generate_note_from_commits(commits)
    if note_body.is_empty():
        if not allow_empty:
            print_warning(
                "No correctly formatted changes detected. "
                "You can use --allow-empty to create a release notes template."
            )
            return
        note_body = generate_empty_note()
        print_warning(
            "No correctly formatted changes detected. "
            "Remember to update the template before releasing the new version."
        )

    # Suggest a new version number based on the changes we found.
    # If this is the first release, starting from "0.0.0".
    version = Version("0.0.0") if latest_tag_name is None else parse(latest_tag_name)
    assert isinstance(version, Version)
    project_name = None
    # Attempts to fetch the name of the project from the README title.
    readme_locations = [
        f"{repo.working_dir}/.github/README.md",
        f"{repo.working_dir}/README.md",
    ]
    for filepath in readme_locations:
        if Path(filepath).is_file():
            with open(filepath, "r", encoding="utf8") as file:
                header = re.search(
                    "^(?: *)#(?: *)(.+)(?: *)$", file.read(), re.MULTILINE
                )
            if header is not None:
                project_name = header.group(1)
                break

    if project_name is None:
        print_warning("No project name found. Release name will not be suggested.")

    try:
        release_phase = _ReleasePhase[phase.upper()]
    except KeyError as err:
        raise RuntimeError(f"Unknown release phase: {phase}.") from err

    query_parameters = {
        "tag": get_new_version_tag(
            release_phase=release_phase,
            current_version=version,
            has_major_changes=len(note_body.major) > 0,
            has_minor_changes=len(note_body.minor) > 0,
        )
    }

    click.echo(f"Suggested version: {query_parameters['tag']}")
    if project_name is not None:
        query_parameters["title"] = f"{project_name} {query_parameters['tag']}"
        click.echo(f"Suggested title: {query_parameters['title']}")
    click.echo("")

    # Create summary of changes.
    change_list = []
    for items, title in [
        (note_body.unknown, "UNKNOWN CHANGES"),
        (note_body.major, "Major changes"),
        (note_body.minor, "Minor changes"),
        (note_body.patch, "Patch changes"),
    ]:
        if not items:
            continue
        change_list += [title]
        formatted_items = [format_list_item(item) for item in items]
        change_list += ["\n".join(formatted_items)]
    query_parameters["body"] = "\n\n".join(change_list)

    click.echo(query_parameters["body"])
    click.echo("")

    if github:
        if len(repo.remotes) == 0:
            print_warning("No remote repo found, cannot redirect to GitHub.")
            return
        if len(repo.remotes) > 1:
            print_warning("More than one remote repo found, cannot redirect to GitHub.")
            return
        match = re.search(
            "^https://github.com/(.*).git$|^git@github.com:(.*).git$",
            repo.remotes.origin.url,
        )
        if match is None:
            print_warning("Remote repository is not on GitHub, cannot redirect.")
            return
        repo_url = f"https://github.com/{match.groups()[0] or match.groups()[1]}"
        parsed_parameters = "&".join(
            [f"{key}={quote_plus(value)}" for key, value in query_parameters.items()]
        )
        if project_name is None:
            print_warning("Project name not found, cannot redirect to GitHub.")
            return
        webbrowser.open(f"{repo_url}/releases/new?{parsed_parameters}")


def _get_commit_info(commit: Commit) -> Optional[_CommitInfo]:
    """
    Extract relevant parts from the commit message.
    """
    message = commit.message
    assert isinstance(message, str)

    title_match = re.match("(?:(?P<kind>[a-z]*)(?P<break>!)?: )?(?P<title>.*)", message)

    # For now, this branch is never triggered since the title group in the
    # regex pattern above will match any string. This mainly serves as
    # a type-checking for mypy at the moment. We can revise this if we
    # change the regex pattern later.
    if title_match is None:
        print_warning(
            f"Commit {commit.hexsha} has incorrectly formatted "
            f"title {message.splitlines()[0]}, ignoring."
        )
        return None

    kind = title_match.groupdict()["kind"]
    title = title_match.groupdict()["title"]

    assert isinstance(title, str)

    # See whether this commit is a breaking change. We need to check both
    # the title for an exclamation mark and the description for BREAKING
    # CHANGE (we check for BREAKING-CHANGE too, as per Conventional
    # Commits).
    breaking_change_message = None
    breaking_description_match = re.search("BREAKING(?: |-)CHANGE:", message)
    if breaking_description_match:
        breaking_change_message = message[breaking_description_match.end() :]
    elif title_match.groupdict()["break"]:
        print_warning(
            f"Commit {commit.hexsha} is missing a breaking change "
            "description, using commit title instead."
        )
        breaking_change_message = convert_to_past_tense(title)

    return _CommitInfo(
        title=title,
        kind=_classify_commit_type(kind),
        sha=commit.hexsha,
        breaking_change_message=breaking_change_message,
    )


def generate_note_from_commits(commits: Iterator[Commit]) -> NoteBody:
    """
    Iterate through commits, collecting information about major, minor, and patch changes.
    """

    note_body = NoteBody()
    for commit in commits:
        commit_info = _get_commit_info(commit)
        if commit_info is None:
            continue
        note_body.add_item(commit_info)
    return note_body


def generate_empty_note() -> NoteBody:
    """
    Create a template for empty release note.
    """
    note_body = NoteBody()
    title = (
        "No changes found. Add a description of the changes that require the release"
    )
    note_body.add_item(
        _CommitInfo(
            title=title, kind=_PrType.PATCH, sha=None, breaking_change_message=None
        )
    )
    return note_body


def get_new_version_tag(
    release_phase: _ReleasePhase,
    current_version: Version,
    has_major_changes: bool,
    has_minor_changes: bool,
) -> str:
    """
    Get the version tag for the next release.
    """
    if release_phase is _ReleasePhase.STABLE:
        _release_func = _stable_release
    else:
        _release_func = partial(_pre_release, phase=release_phase)
    return _release_func(
        current_version,
        has_major_changes=has_major_changes,
        has_minor_changes=has_minor_changes,
    )


def _pre_release(
    current_version: Version,
    has_major_changes: bool,
    has_minor_changes: bool,
    phase: _ReleasePhase,
) -> str:
    if current_version.is_prerelease:
        assert current_version.pre is not None  # for mypy
        current_pre_version, pre_version_num = current_version.pre
        if current_pre_version == "b" and phase is _ReleasePhase.ALPHA:
            print_warning(
                "Releasing an alpha version after a beta version means "
                "a stable version is skipped."
            )
        # Jumping between pre release phases would reset the pre version number.
        _num = 0 if current_pre_version != phase.value[0] else pre_version_num + 1
        return f"{current_version.base_version}-{phase.value}.{_num}"
    return f"{_stable_release(current_version, has_major_changes, has_minor_changes)}-{phase.value}"


def _stable_release(
    current_version: Version, has_major_changes: bool, has_minor_changes: bool
) -> str:
    # pre -> stable
    if current_version.is_prerelease:
        return current_version.base_version

    # stable -> stable
    major, minor, patch = current_version.release
    if has_major_changes:
        if major > 0:
            major += 1
            minor = 0
            patch = 0
        else:
            minor += 1
            patch = 0
    elif has_minor_changes:
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def convert_to_past_tense(text: str) -> str:
    """
    Tries to convert the given text to past tense.
    """
    # Convert the first word to past tense if possible, otherwise just leave the
    # text unchanged.
    parts = text.split(" ", 1)
    past_tense = pyinflect.getInflection(parts[0], "VBD")
    if past_tense:
        parts[0] = past_tense[0]
    return " ".join(parts)


def format_list_item(text: str) -> str:
    """
    Formats text (which might contain newlines) into a Markdown list item.
    """
    text = text.strip()

    # Capitalize first word and add period if necessary.
    parts = text.split(" ", 1)
    parts[0] = parts[0].capitalize()
    text = " ".join(parts)
    if text[-1] not in ".?!":
        text += "."

    # Indent subsequent lines.
    indented = "\n  ".join([line.strip() for line in text.splitlines()])

    return f"- {indented}"


def print_warning(message: str):
    """
    Prints a warning message to stderr.
    """
    click.echo(click.style(message, fg="red"), err=True)
