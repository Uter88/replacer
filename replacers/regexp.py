import re

from .type_defs import Replacements, ReplaceResult


class RegexpReplacer:
    """Regular expression string replacer.

    Effective on small and middle datasets.

    Complexity:
        O(N): where N = len(line)

    Attributes:
        pattern (re.Pattern): Compiled regexp pattern from replacements pairs.
        replacements (Replacements): Replacements pairs.
    """

    pattern: re.Pattern
    replacements: Replacements

    def __init__(self, replacements: Replacements):
        """Constructor.
        If no replacements - compile a regular expression that will never work.
        Otherwise compile regular expression from escaped replacements keys.

        Args:
            replacements (Replacements): _description_
        """

        if not replacements:
            self.pattern = re.compile(r"(?!)")
        else:
            regexp = "|".join([re.escape(key) for key in replacements])
            self.pattern = re.compile(regexp)

        self.replacements = replacements

    def apply(self, line: str) -> ReplaceResult:
        """
        Apply regular expression replacements.

        Args:
            line (str): Line to replace.

        Returns:
            ReplaceResult: Replaced line and replacing count.
        """

        if not line or not self.replacements:
            return line, 0

        replaced_chars = 0

        def repl(match: re.Match) -> str:
            nonlocal replaced_chars
            key = match.group(0)
            replaced_chars += len(key)
            return self.replacements[key]

        replaced_line = self.pattern.sub(repl, line)

        return replaced_line, replaced_chars

    def __call__(self, line: str, _: Replacements) -> ReplaceResult:
        """Call apply"""

        return self.apply(line)
