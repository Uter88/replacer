from typing import Tuple, Callable, OrderedDict
from enum import Enum

ReplaceResult = Tuple[str, int]
Replacer = Callable[[str, OrderedDict[str, str]], ReplaceResult]
Replacements = OrderedDict[str, str]


class ReplaceMethod(str, Enum):
    """Replace method.

    Attributes:
        CASCADING: Cascading replacing.
        SINGLE_PASS: Single pass replacing.
        REGEXP: Regular expression replacing.
        AHO_CORASICK: Aho-Corasick algorithm replacing.
    """

    CASCADING = "cascading"
    SINGLE_PASS = "single_pass"
    REGEXP = "regexp"
    AHO_CORASICK = "aho_corasick"
