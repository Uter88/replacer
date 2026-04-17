import sys
import argparse
from pathlib import Path
from typing import Tuple, List, Iterable

from replacers.type_defs import ReplaceMethod, Replacements


class ConfigLineParseError(Exception):
    """Parse config line exception"""


def _parse_config_line(line: str) -> Tuple[str, str]:
    """Parse config line.

    Allows only key=value format.
    Raises exception if key and value is empty or equals.

    Args:
        line (str): Raw config line.

    Raises:
        ConfigLineParseError: Config line parse error.

    Returns:
        ConfigLine: Parsed line of config.
    """

    if "=" not in line:
        raise ConfigLineParseError("expected 'key=value' format")

    key, value = line.split("=", 1)
    key, value = key.strip(), value.strip()

    if not key:
        raise ConfigLineParseError("key is empty")

    if not value:
        raise ConfigLineParseError("value is empty")

    if key == value:
        raise ConfigLineParseError("key and value are the same")

    return (key, value)


def parse_replacements(config_lines: Iterable[str]) -> Replacements:
    """Parse replacements from config file.
    Ignore empty and invalid lines.

    Args:
        config_lines (Iterable[str]): Config lines iterator.

    Returns:
        Replacements: Parsed replacements pairs from config file.
    """

    replacements: Replacements = Replacements()
    errors: List[str] = []

    for i, line in enumerate(config_lines, start=1):
        line = line.strip()

        if not line:
            continue

        try:
            (key, value) = _parse_config_line(line)
            replacements[key] = value
        except ConfigLineParseError as e:
            errors.append(f"Line {i}: {e}. Ignoring")

    if not replacements:
        errors.append("No valid key=value pairs found in config file")

    if errors:
        msg = "\n\t".join(errors)
        print("Parsing config errors:\n\t" + msg, file=sys.stderr)

    return replacements


def parse_file_exception(e: Exception) -> str:
    """Parse file processing exception.

    Args:
        e (Exception): Caused exception.

    Returns:
        str: Error description.
    """

    if isinstance(e, FileNotFoundError):
        return f"file not found: {e.filename}"

    if isinstance(e, PermissionError):
        return f"permission denied: {e.filename}"

    if isinstance(e, IsADirectoryError):
        return f"expected file, found directory: {e.filename}"

    if isinstance(e, OSError):
        return f"I/O error ({e.errno}): {e.strerror}"

    if isinstance(e, UnicodeDecodeError):
        return f"decoding error at position {e.start}: file is not UTF-8 encoded"

    return f"unexpected error: {e}"


def parse_command_line_args() -> Tuple[Path, Path, ReplaceMethod]:
    """Parse command line args.

    Returns:
        Tuple[Path, Path, ReplaceMethod]: Config/sample path and replace method.
    """

    parser = argparse.ArgumentParser(description="Replacer")
    parser.add_argument("config", help="Config file path", type=Path)
    parser.add_argument("sample", help="Sample file path", type=Path)
    parser.add_argument(
        "--method",
        choices=[m.value for m in ReplaceMethod],
        help="Replacing method",
        default=ReplaceMethod.CASCADING.value,
        type=ReplaceMethod,
    )

    args = parser.parse_args()

    if args.config == args.sample:
        print("Config and sample files must be different", file=sys.stderr)
        sys.exit(1)

    return args.config, args.sample, args.method
