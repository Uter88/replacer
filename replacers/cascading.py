from .type_defs import ReplaceResult, Replacements


def cascading_replacer(line: str, replacements: Replacements) -> ReplaceResult:
    """
    Apply cascade replacements, each rule operates on the result of the previous.
    This may lead to double-counting if a later rule replaces characters that were
    introduced by an earlier rule.

    Complexity:
        O(K * L) where K = len(replacements), L = current line length.
        In the worst case, L can increase significantly, but the number of passes along the line will remain O(K).

    Args:
        line (str): Line to replace.
        replacements (Replacements): Replacement pairs.

    Returns:
        ReplaceResult: Replaced line and replacing count.
    """

    total_replaced = 0

    for key, val in replacements.items():
        if key not in line:
            continue

        count = line.count(key)
        new_line = line.replace(key, val)
        total_replaced += count * len(key)
        line = new_line

    return line, total_replaced
