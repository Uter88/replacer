import sys

from parsers import parse_command_line_args, parse_replacements, parse_file_exception

from replacers import (
    apply_replacing,
    get_replacer_by_method,
    write_output_lines,
)


def main():
    config_path, sample_path, replace_method = parse_command_line_args()

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            replacements = parse_replacements(config_file)
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error proceed config file: {parse_file_exception(e)}", file=sys.stderr)
        sys.exit(1)

    if not replacements:
        print("No valid replacements found. Exiting.", file=sys.stderr)
        sys.exit(1)

    replacer = get_replacer_by_method(replace_method, replacements)

    try:
        with open(sample_path, "r", encoding="utf-8") as sample_file:
            changed_lines, unchanged_lines = apply_replacing(
                sample_file, replacements, replacer
            )
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error proceed sample file: {parse_file_exception(e)}", file=sys.stderr)
        sys.exit(1)

    write_output_lines(changed_lines, unchanged_lines)


if __name__ == "__main__":
    main()
