from typing import List

from .type_defs import Replacements, ReplaceResult


def single_pass_replacer(line: str, replacements: Replacements) -> ReplaceResult:
    """Apply replacements in a single left-to-right pass with non-overlapping matches.

    It has low efficiency. It is recommended to use other methods.

    Complexity:
        O(L * K) where L = len(line), K = len(replacements).
        In the worst case checks each rule for each position.

    Args:
        line (str): Line to replace.
        replacements (Replacements): Replacement pairs.

    Returns:
        ReplaceResult: Replaced line and replacing count.
    """

    if not line or not replacements:
        return line, 0

    i, n = 0, len(line)
    result_parts: List[str] = []
    total_replaced = 0

    while i < n:
        matched = False

        for key, val in replacements.items():
            if line.startswith(key, i):
                result_parts.append(val)
                total_replaced += len(key)
                i += len(key)
                matched = True
                break

        if not matched:
            result_parts.append(line[i])
            i += 1

    return "".join(result_parts), total_replaced
