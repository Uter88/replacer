from typing import Tuple, List, TextIO, Iterable
import sys

from .aho_corasick import AhoCorasickReplacer, AhoCorasickReplacerC
from .cascading import cascading_replacer
from .single_pass import single_pass_replacer
from .regexp import RegexpReplacer
from .type_defs import ReplaceMethod, Replacer, Replacements, ReplaceResult


def get_replacer_by_method(
    method: ReplaceMethod, replacements: Replacements
) -> Replacer:
    """Get replacer by specified method.

    Args:
        method (ReplaceMethod): Replacing method.
        replacements (Replacements): Replacements pairs.

    Returns:
        Replacer: Characters replacer.
    """

    if method == ReplaceMethod.CASCADING:
        return cascading_replacer

    if method == ReplaceMethod.SINGLE_PASS:
        return single_pass_replacer

    if method == ReplaceMethod.REGEXP:
        return RegexpReplacer(replacements)

    if method == ReplaceMethod.AHO_CORASICK:
        return AhoCorasickReplacer(replacements)

    if method == ReplaceMethod.AHO_CORASICK_C:
        return AhoCorasickReplacerC(replacements)

    raise ValueError("Invalid replacer method")


def write_output_lines(
    changed: List[ReplaceResult], unchanged: List[str], output: TextIO = sys.stdout
):
    """Write output lines result.

    Args:
        changed (List[ReplaceResult]): Changed lines.
        unchanged (List[str]): Unchanged lines.
        output (Optional[TextIO]): Output. Defaults to sys.stdout.
    """

    changed.sort(key=lambda x: x[1], reverse=True)

    for line, _ in changed:
        output.write(line + "\n")

    for line in unchanged:
        output.write(line + "\n")


def apply_replacing(
    lines: Iterable[str], replacements: Replacements, replacer: Replacer
) -> Tuple[List[ReplaceResult], List[str]]:
    """Replace characters in input file.

    Args:
        lines (Iterable[str]): Input lines.
        replacements (Replacements): Replacements pairs.
        replacer (Replacer): Character replacer.

    Returns:
        Tuple[List[ReplaceResult], List[str]]: Replaced and unreplaced lines.
    """

    changed_lines: List[ReplaceResult] = []
    unchanged_lines: List[str] = []

    for line in lines:
        line = line.rstrip("\n\r")

        replaced_line, replaced_chars = replacer(line, replacements)

        if replaced_chars > 0:
            changed_lines.append((replaced_line, replaced_chars))
        else:
            unchanged_lines.append(line)

    return changed_lines, unchanged_lines


__all__ = [
    "get_replacer_by_method",
    "write_output_lines",
    "apply_replacing",
    "RegexpReplacer",
    "AhoCorasickReplacer",
    "AhoCorasickReplacerC",
    "cascading_replacer",
    "single_pass_replacer",
    "ReplaceMethod",
    "Replacements",
    "ReplaceResult",
    "Replacer",
]
