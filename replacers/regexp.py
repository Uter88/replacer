import re

from .type_defs import Replacements, ReplaceResult


class RegexpReplacer:
    """Regular expression string replacer.

    Attributes:
        pattern (re.Pattern): Compiled regexp pattern from replacements pairs.
        replacements (Replacements): Replacements pairs.
    """

    pattern: re.Pattern
    replacements: Replacements

    def __init__(self, replacements: Replacements):
        if not replacements:
            self.pattern = re.compile(r"(?!)")
        else:
            regexp = "|".join([re.escape(key) for key in replacements])
            self.pattern = re.compile(regexp)

        self.replacements = replacements

    def apply(self, line: str) -> ReplaceResult:
        """
        Apply regular expression replacements.

        Complexity:
            O(N) where N = len(line).

        Args:
            line (str): Line to replace.

        Returns:
            ReplaceResult: Replaced line and replacing count.
        """

        replaced_chars = 0

        def repl(match: re.Match) -> str:
            nonlocal replaced_chars
            key = match.group(0)
            replaced_chars += len(key)
            return self.replacements[key]

        new_s = self.pattern.sub(repl, line)

        return (new_s, replaced_chars)

    def __call__(self, line: str, _: Replacements) -> ReplaceResult:
        """Call apply"""

        return self.apply(line)
