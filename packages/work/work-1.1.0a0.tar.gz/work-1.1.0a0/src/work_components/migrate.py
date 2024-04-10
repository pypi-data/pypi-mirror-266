"""Temporary migration code between program versions."""

import codecs
import pathlib
import re
import textwrap
from typing import Dict

from work_components import consts
from work_components.protocols import IFlags

# Remove in v0.103 #


def noop_no_aliases_set():
    """Mark migration of aliases to new configurable mode. Does nothing to reduce complexity."""


def move_config_file(new_path: pathlib.Path):
    """Move config file to expected path."""
    old_path = pathlib.Path("~/.workrc").expanduser()
    if not old_path.exists():
        return

    if new_path.exists():
        print(
            f'Configuration file is now at "{new_path}", but obsolescent file '
            f'"{old_path}" was found; you can safely remove the latter.'
        )
        return

    # <Windows-specific> ~/.config does not exist by default
    if not new_path.parent.exists():
        new_path.parent.mkdir(parents=True)

    old_path.rename(new_path)
    print(
        textwrap.indent(
            f"\nImportant – your configuration file was moved!\n"
            f"  Old path: {old_path}\n"
            f"  New path: {new_path}\n"
            "See release notes of v0.100 for more information.\n",
            "  ",
        )
    )


# Remove in v0.104 #


def noop_records_encoding():
    """Mark conversion of records. Does nothing to prevent circular import."""


def check_and_convert_textfile(file: pathlib.Path) -> None:
    """Check given file for encoding and newlines.
    Ensure UTF-8 and \\n-newlines."""

    # Encoding: Try to open and read in UTF-8. If it fails, it isn't UTF-8
    try:
        file_bytes = file.read_bytes()
        codecs.decode(file_bytes, encoding="utf-8")
    except UnicodeDecodeError:
        # Silent handling (otherwise, user would be spammed)
        contents = file.read_text()
        file.write_text(contents, encoding="utf-8")

        print(f"Encoding of file {file.name} converted to UTF-8")

    # Newlines: Open in default mode, store in newline-enforced mode.
    with file.open(encoding="utf-8") as file_h:
        lines = file_h.readlines()
    # Newline mode not necessary to be specified here, just for clarity.
    with file.open(mode="w", encoding="utf-8", newline="\n") as file_h:
        # Lines are converted automatically above, when reading.
        file_h.writelines(lines)


# Remove in v1 #


def raise_old_protocol_version(row):
    """Raise if row only has two elements (no category and message).
    To be removed in v1.
    """
    if len(row) == 2:
        raise IOError(
            "Detected old protocol version. "
            "Please migrate using v0.93 and then try again."
        )


def noop_expected_hours_none():
    """Mark migration of expected hours. Does nothing to prevent cyclic dependencies."""
    return


def upgrade_info_file(file, update_function) -> bool:
    """Upgrade info file to new format, which includes the program version."""
    file.seek(0)
    file_content = file.read()
    match = re.fullmatch(consts.INFO_FILE_PATTERN, file_content)
    if not match:
        return False

    update_function(int(match.group(3)))
    print("Info file upgraded to new format.")
    return True


# Keep #


def print_whats_new_in(version: str, flags: IFlags):
    """Print 'what's new' message for given version."""
    whatsnew_messages: Dict[str, Dict[str, str]] = {
        "0": {
            "100": """Configurable aliases and macros
Configuration file location moved to match XDG Base Directory Specification
Force rounding with arguments "now+", "now-", or prevent with "now!"
Improved listing of free days in "free-days --list" """,
        },
        "1": {
            "0": """New name on PyPI: work-time-log is now work!
Skip interactive selection (edit, remove) with --all or --last
Filtering applies smart case
Day names and dates can be used interchangeably
Flags --date and -D are deprecated""",
        },
    }

    major, minor, *_ = version.split(".")
    if major not in whatsnew_messages or minor not in whatsnew_messages[major]:
        return

    message_shown_flag: str = f"whatsnew:{major}.{minor}"
    if flags.is_set(message_shown_flag):
        return
    flags.set(message_shown_flag)

    print(
        f"work has been upgraded to version {major}.{minor}!\n\n"
        "Here's a summary of what's new:"
    )
    print(textwrap.indent(whatsnew_messages[major][minor], "  - "))
    print("\nRead more: https://vauhoch.zett.cc/work/releases/\n")
