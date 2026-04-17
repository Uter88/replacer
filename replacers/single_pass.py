from typing import List

from .type_defs import Replacements, ReplaceResult


def single_pass_replacer(line: str, replacements: Replacements) -> ReplaceResult:
    """Apply replacements in a single left-to-right pass with non-overlapping matches.

    Complexity:
        O(L * K) where L = len(line), K = len(replacements).
        In the worst case checks each rule for each position.

    Args:
        line (str): Line to replace.
        replacements (Replacements): Replacement pairs.

    Returns:
        ReplaceResult: Replaced line and replacing count.
    """

    i, n = 0, len(line)
    result: List[str] = []
    total_replaced = 0

    while i < n:
        matched = False

        for key, val in replacements.items():
            if line.startswith(key, i):
                result.append(val)
                total_replaced += len(key)
                i += len(key)
                matched = True
                break

        if not matched:
            result.append(line[i])
            i += 1

    return "".join(result), total_replaced
