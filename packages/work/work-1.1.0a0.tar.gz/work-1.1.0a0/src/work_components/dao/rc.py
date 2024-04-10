#!/usr/bin/env python3

# pylint: disable-msg=invalid-name

""" The DAO for the runtime configuration file. """

import json
from collections import ChainMap
from typing import IO, Any, Callable, Dict, List, Mapping, MutableMapping, Optional

from work_components import consts, migrate, util
from work_components.arguments import MODES
from work_components.consts import RC_FILE
from work_components.protocols import IFlags

# When a new key is to be added:
# - Add key string as class variable
# - Add default value to default_config
# - Implement check in _ensure_config_correctness()
#
# In work.py:
# - Add actual functionality related to the configuration
# - (optional) Add see target to see()


TIME_FORMAT = "%H:%M"


class RCError(OSError):
    """Error in runtime configuration file"""

    def __init__(self, msg):
        super().__init__("RC file erroneous! {}".format(msg))


class RC:
    """Runtime configuration"""

    expected_hours_k = "expected_hours"
    aliases_k = "aliases"
    macros_k = "macros"

    default_config: Dict[str, Any] = {
        expected_hours_k: dict(zip(consts.WEEKDAYS, [8.0] * 5 + [0.0] * 2)),
        aliases_k: {
            "status": ["s"],
            "hours": ["h"],
            "list": ["ls"],
            "edit": ["e"],
            "remove": ["rm"],
        },
        macros_k: {
            "day": "list --include-active --with-breaks --list-empty",
            "macros": "config --see macros",  # aliases can be seen with work -h
        },
    }

    def __init__(self, user_config: Optional[Dict] = None):
        """Constructor. Initializes config with default values.
        If `user_config` is given, it will be prepended to the internal `ChainMap`."""

        user_config = user_config or {}
        RC._ensure_config_correctness(user_config, ensure_completeness=False)

        try:
            RC._ensure_config_correctness(RC.default_config, ensure_completeness=True)
        except RCError as rc_err:
            raise RuntimeError("Invalid default configuration") from rc_err

        self._config = ChainMap(user_config, RC.default_config)

    @property
    def expected_hours(self) -> Dict[str, float]:
        """The hours expected on each day of the week."""
        return self._config[RC.expected_hours_k]

    @expected_hours.setter
    def expected_hours(self, value: Dict[str, float]):
        self._config[RC.expected_hours_k] = value

    @property
    def aliases(self) -> Dict[str, List[str]]:
        """Aliases for work commands."""
        return self._config[RC.aliases_k]

    @property
    def macros(self) -> Dict[str, str]:
        """Macros that expand to command and argument(s) or flag(s)."""
        return self._config[RC.macros_k]

    @property
    def _user_config(self) -> MutableMapping:
        """In-memory representation of the user configuration."""
        return self._config.maps[0]

    ### I/O ###

    def dump(self, rc_file: IO) -> None:
        """Write this RC's user configuration to file."""

        # Data have been verified on instantiation
        json.dump(self._user_config, rc_file, indent="\t", ensure_ascii=False)

    @staticmethod
    def load(rc_file):
        # type: (IO) -> RC
        """Load an RC from file and instantiate an RC."""

        try:
            user_config = json.load(rc_file)
        except json.JSONDecodeError as json_err:
            raise RCError(
                f"Invalid JSON encountered around line {json_err.lineno} – did you "
                "forget quotes or add an (invalid) trailing comma to a list?"
            ) from json_err

        if user_config.get(RC.expected_hours_k, -1) is None:
            migrate.noop_expected_hours_none()
            del user_config[RC.expected_hours_k]
            print(
                util.wrap_and_indent(
                    "\n",
                    (
                        f'Found value "null" for key "{RC.expected_hours_k}" in'
                        "configuration file. Since v0.100, you do not need to "
                        'explicitly set a configuration item to "None" to force'
                        "use of the default config. Instead, omitting the item "
                        "will suffice."
                    ),
                    "\n",
                    (
                        "Configuration file has been updated: key "
                        f'"{RC.expected_hours_k}" was deleted.'
                    ),
                    "\n",
                    prefix="  ",
                )
            )
            with RC_FILE.open("w", encoding="utf-8", newline="\n") as rc_file_writable:
                RC(user_config).dump(rc_file_writable)

        return RC(user_config)

    def migrate(self, flags: IFlags) -> None:
        """Optional migrations for convenience."""

        # <MIGRATE-aliases> functionality. To be removed in v0.103!
        migration_flag: str = "rc:aliases_migrated"
        if flags.is_set(migration_flag):
            return

        migrated: bool = False
        if RC.aliases_k not in self._user_config:
            migrate.noop_no_aliases_set()
            self._user_config[RC.aliases_k] = {
                "switch": ["pause"],
                "status": ["s"],
                "hours": ["h"],
                "list": ["ls"],
                "edit": ["e"],
                "remove": ["rm"],
                "free-days": ["recess"],
            }
            migrated = True
        if RC.macros_k not in self._user_config:
            self._user_config[RC.macros_k] = {
                "day": "list --include-active --with-breaks --list-empty",
                "macros": "config --see macros",
            }
            migrated = True

        flags.set(migration_flag)
        if not migrated:
            return

        print(
            util.wrap_and_indent(
                "\n",
                (
                    "Found unconfigured aliases/macros. Since v0.100, aliases "
                    "can be configured via the configuration file. Not all "
                    "existing aliases will be migrated, therefore the old "
                    "aliases/macros were added to your user configuration."
                ),
                "\n",
                "Configuration file has been updated: aliases were added.",
                "\n",
                prefix="  ",
            )
        )

        with RC_FILE.open("w", encoding="utf-8", newline="\n") as rc_file_writable:
            self.dump(rc_file_writable)

    ### Static methods ###

    @staticmethod
    def default_rc_content() -> str:
        """Create the contents of an example RC file, setting all keys."""
        return json.dumps(RC.default_config, indent="\t")

    @staticmethod
    def load_rc():  # -> RC
        """Load a RC. If any RC file exists, retrieve it. If not, creates a basic file."""

        migrate.move_config_file(new_path=RC_FILE)

        if not RC_FILE.exists():
            with RC_FILE.open("w", encoding="utf-8", newline="\n") as rc_file:
                rc_file.write(RC.default_rc_content())
            print(
                f"Configuration file with default values created at {RC_FILE}\n"
                "  Check and edit the file with $EDITOR (work config --path).\n"
            )

        with RC_FILE.open("r", encoding="utf-8") as rc_file:
            return RC.load(rc_file)

    @staticmethod
    def _ensure_config_correctness(data: Mapping, ensure_completeness: bool) -> None:
        """Ensure that the mapping is fit for JSON (de)serialization. Raises if not."""

        expected_keys: List[str] = [RC.expected_hours_k, RC.aliases_k, RC.macros_k]
        if ensure_completeness:
            for k in expected_keys:
                if k not in data:
                    raise RCError(f'Missing expected key "{k}"')

        for k in data:
            if k not in expected_keys:
                raise RCError(f'Unexpected key "{k}"')

        verifiers: Dict[str, Callable] = {
            RC.expected_hours_k: RC._verify_expected_hours,
            RC.aliases_k: RC._verify_aliases,
            RC.macros_k: RC._verify_macros,
        }

        for key, verifier in verifiers.items():
            if key in data:
                verifier(data[key])

    @staticmethod
    def _verify_expected_hours(expected_hours) -> None:
        """Verify the value for expected hours. Raises RCError if invalid."""

        # Should be a mapping of day to hours: { "Monday": 8.0, Tuesday: 0.0, ... }
        if not isinstance(expected_hours, Mapping):
            raise RCError(f'"{RC.expected_hours_k}" expects a mapping.')

        if unexpected_days := set(expected_hours.keys()) - set(consts.WEEKDAYS):
            raise RCError(
                f'Unexpected key(s) for "{RC.expected_hours_k}": '
                + ", ".join(unexpected_days)
                + f"; expects one of: {', '.join(consts.WEEKDAYS)}"
            )

        if list(expected_hours.keys()) != consts.WEEKDAYS:
            raise RCError(
                f'Keys for "{RC.expected_hours_k}" are sorted incorrectly; '
                + f"expects: {', '.join(consts.WEEKDAYS)}"
            )

        if missing_days := set(consts.WEEKDAYS) - set(expected_hours.keys()):
            raise RCError(
                f'Missing expected key(s) for "{RC.expected_hours_k}": '
                + ", ".join(missing_days)
            )

        min_hours, max_hours = consts.ALLOWED_WORK_HOURS
        if invalid_hours := [
            expected_hour_value
            for expected_hour_value in expected_hours.values()
            if expected_hour_value < min_hours or expected_hour_value > max_hours
        ]:
            raise RCError(
                f'Invalid value(s) for "{RC.expected_hours_k}": '
                + ", ".join([str(i_h) for i_h in invalid_hours])
                + f"; expects values in ({min_hours}, {max_hours})."
            )

    @staticmethod
    def _verify_aliases(aliases) -> None:
        """Verify the value for aliases. Raises RCError if invalid."""

        # Should be a mapping of commands to list of aliases: { "status": ["s"], "edit": [] }
        if not isinstance(aliases, Mapping):
            raise RCError(f'"{RC.aliases_k}" expects a mapping.')

        for key in aliases.keys():
            if key not in MODES:
                raise RCError(
                    f'Key "{key}" is not a valid command name. '
                    f"Must be one of: {MODES.keys()}"
                )

        for value in aliases.values():
            if not isinstance(value, list):
                raise RCError(f"Expected a list; got: {value}")

    @staticmethod
    def _verify_macros(macros) -> None:
        """Verify the value for macros. Raises RCError if invalid."""

        # Should be a mapping of commands to list of aliases: { "status": ["s"], "edit": [] }
        if not isinstance(macros, Mapping):
            raise RCError(f'"{RC.macros_k}" expects a mapping.')

        for key, value in macros.items():
            if key.startswith("-"):
                raise RCError(f'Macros may not start with "-"; found: "{key}"')

            if key in MODES:
                raise RCError(
                    f'Macros may not override existing commands; found: "{key}"'
                )

            if not isinstance(value, str):
                raise RCError(f"Expected a string; got: {value}")

            if "  " in value:
                raise RCError(f'Macro "{key}" contains extra spaces: "{value}"')
