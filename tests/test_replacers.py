import unittest
from io import StringIO
from abc import ABC, abstractmethod

from replacers import (
    get_replacer_by_method,
    apply_replacing,
    write_output_lines,
)
from replacers.cascading import cascading_replacer
from replacers.single_pass import single_pass_replacer
from replacers.regexp import RegexpReplacer
from replacers.aho_corasick import AhoCorasickReplacer, AhoCorasickReplacerC
from replacers.type_defs import ReplaceMethod, Replacements, Replacer


class BaseReplacerTest(unittest.TestCase, ABC):

    @abstractmethod
    def make_replacer(self, replacements: Replacements) -> Replacer:
        raise NotImplementedError

    def test_empty_line(self):
        """Testing case: empty line"""

        line = ""
        replacements = Replacements()

        replacer = self.make_replacer(replacements)
        result, count = replacer(line, replacements)
        self.assertEqual(result, line)
        self.assertEqual(count, 0)

    def test_no_replacements(self):
        """Testing case: no replacements"""

        line = "hello"
        replacements = Replacements()

        replacer = self.make_replacer(replacements)
        result, count = replacer(line, replacements)
        self.assertEqual(result, line)
        self.assertEqual(count, 0)

    def test_simple_replacement(self):
        """Testing case: simple replacement"""

        line = "ab"
        expected_line, expected_count = "X", 2
        replacements = Replacements([("ab", "X")])

        replacer = self.make_replacer(replacements)
        result, count = replacer(line, replacements)
        self.assertEqual(result, expected_line)
        self.assertEqual(count, expected_count)


class BaseNonOverlappingTest(BaseReplacerTest, ABC):

    def test_non_overlapping(self):
        """Testing case: non-overlapping replacement"""

        line = "abab"
        expected_line, expected_count = "XX", 4
        replacements = Replacements([("ab", "X")])

        replacer = self.make_replacer(replacements)
        result, count = replacer(line, replacements)
        self.assertEqual(result, expected_line)
        self.assertEqual(count, expected_count)

    def test_prefix_priority(self):
        """Testing case: prefix with hight priority"""

        line = "ab"
        expected_line, expected_count = "X", 2
        replacements = Replacements([("ab", "X"), ("a", "Z")])

        replacer = self.make_replacer(replacements)
        result, count = replacer(line, replacements)
        self.assertEqual(result, expected_line)
        self.assertEqual(count, expected_count)

    def test_overlapping_priority_by_order(self):
        """Testing case: overlapping by ordering"""

        line = "abc"
        expected_line, expected_count = "Xc", 2
        replacements = Replacements([("ab", "X"), ("bc", "Y")])

        replacer = self.make_replacer(replacements)
        result, count = replacer(line, replacements)
        self.assertEqual(result, expected_line)
        self.assertEqual(count, expected_count)


class TestCascadingReplacer(BaseReplacerTest):
    """Testing cascading_replacer"""

    def make_replacer(self, replacements: Replacements) -> Replacer:
        return cascading_replacer

    def test_cascading_effect(self):
        """Testing case: cascading replacement, when next replacement affect previous"""

        line = "a"
        expected_line, expected_count = "c", 2
        replacements = Replacements([("a", "b"), ("b", "c")])

        replacer = self.make_replacer(replacements)
        result, count = replacer(line, replacements)
        self.assertEqual(result, expected_line)
        self.assertEqual(count, expected_count)


class TestSinglePassReplacer(BaseNonOverlappingTest):

    def make_replacer(self, replacements: Replacements) -> Replacer:
        return single_pass_replacer

    def test_keep_unmatched_chars(self):
        """Testing case: keep unmatched chars"""

        line = "cab"
        expected_line, expected_count = "cX", 2
        replacements = Replacements([("ab", "X")])

        replacer = self.make_replacer(replacements)
        result, count = replacer(line, replacements)
        self.assertEqual(result, expected_line)
        self.assertEqual(count, expected_count)


class TestRegexpReplacer(BaseNonOverlappingTest):

    def make_replacer(self, replacements: Replacements) -> Replacer:
        return RegexpReplacer(replacements)

    def test_regexp_special_chars_escaped(self):
        """Testing case: escape special characters"""

        line = "a.b c?d"
        expected_line, expected_count = "X Y", 3 + 3
        replacements = Replacements([("a.b", "X"), ("c?d", "Y")])

        replacer = self.make_replacer(replacements)
        result, count = replacer(line, replacements)
        self.assertEqual(result, expected_line)
        self.assertEqual(count, expected_count)


class TestAhoCorasickReplacer(BaseNonOverlappingTest):

    def make_replacer(self, replacements: Replacements) -> Replacer:
        return AhoCorasickReplacer(replacements)

    def test_prefix_priority_reverse(self):
        """Test case: prefix with hight priority reversed"""

        replacements = Replacements([("a", "Z"), ("ab", "X")])
        replacer = self.make_replacer(replacements)

        result, count = replacer("ab", replacements)
        self.assertEqual(result, "Zb")
        self.assertEqual(count, 1)

    def test_multiple_matches_in_one_position(self):
        """Test case: multiple matches in same position"""

        replacements = Replacements([("ab", "X"), ("a", "Z")])
        replacer = self.make_replacer(replacements)

        result, count = replacer("ab", replacements)
        self.assertEqual(result, "X")
        self.assertEqual(count, 2)


class TestAhoCorasickReplacerC(BaseNonOverlappingTest):

    def make_replacer(self, replacements: Replacements) -> Replacer:
        return AhoCorasickReplacerC(replacements)

    def test_prefix_priority_reverse(self):
        """Test case: prefix with hight priority reversed"""

        replacements = Replacements([("a", "Z"), ("ab", "X")])
        replacer = self.make_replacer(replacements)

        result, count = replacer("ab", replacements)
        self.assertEqual(result, "Zb")
        self.assertEqual(count, 1)

    def test_multiple_matches_in_one_position(self):
        """Test case: multiple matches in same position"""

        replacements = Replacements([("ab", "X"), ("a", "Z")])
        replacer = self.make_replacer(replacements)

        result, count = replacer("ab", replacements)
        self.assertEqual(result, "X")
        self.assertEqual(count, 2)


class TestGetReplacerByMethod(unittest.TestCase):
    """Testing get_replacer_by_method"""

    def test_cascading(self):
        """Test case: get cascading_replacer"""

        replacer = get_replacer_by_method(ReplaceMethod.CASCADING, Replacements())
        self.assertIs(replacer, cascading_replacer)

    def test_single_pass(self):
        """Test case: get single_pass_replacer"""

        replacer = get_replacer_by_method(ReplaceMethod.SINGLE_PASS, Replacements())
        self.assertIs(replacer, single_pass_replacer)

    def test_regexp(self):
        """Test case: get RegexpReplacer"""

        replacements = Replacements([("a", "b")])
        replacer = get_replacer_by_method(ReplaceMethod.REGEXP, replacements)
        self.assertIsInstance(replacer, RegexpReplacer)

    def test_aho_corasick(self):
        """Test case: get AhoCorasickReplacer"""

        replacements = Replacements([("a", "b")])
        replacer = get_replacer_by_method(ReplaceMethod.AHO_CORASICK, replacements)
        self.assertIsInstance(replacer, AhoCorasickReplacer)


class TestApplyReplacing(unittest.TestCase):
    """Testing apply_replacing"""

    def test_empty_lines(self):
        """Test case: empty lines"""

        lines = []
        changed, unchanged = apply_replacing(lines, Replacements(), cascading_replacer)
        self.assertEqual(changed, [])
        self.assertEqual(unchanged, [])

    def test_all_changed(self):
        """Test case: all lines is changed"""

        lines = ["ab", "cd"]
        replacements = Replacements([("ab", "X"), ("cd", "Y")])
        changed, unchanged = apply_replacing(lines, replacements, cascading_replacer)
        self.assertEqual(len(changed), 2)
        self.assertEqual(changed[0][0], "X")
        self.assertEqual(changed[1][0], "Y")
        self.assertEqual(unchanged, [])

    def test_mixed(self):
        """Test case: changed and unchanged lines"""

        lines = ["ab", "nochange", "cd"]
        replacements = Replacements([("ab", "X"), ("cd", "Y")])
        changed, unchanged = apply_replacing(lines, replacements, cascading_replacer)
        self.assertEqual(len(changed), 2)
        self.assertEqual(changed[0][0], "X")
        self.assertEqual(changed[1][0], "Y")
        self.assertEqual(unchanged, ["nochange"])

    def test_strip_newline(self):
        """Test case: strip new line symbol"""

        lines = ["ab\n", "cd\n"]
        replacements = Replacements([("ab", "X")])
        changed, unchanged = apply_replacing(lines, replacements, cascading_replacer)
        self.assertEqual(changed[0][0], "X")
        self.assertEqual(unchanged, ["cd"])


class TestWriteOutputLines(unittest.TestCase):
    """Testing write_output_lines"""

    def setUp(self):
        self.output = StringIO()

    def test_empty_lists(self):
        """Test case: empty lines"""

        write_output_lines([], [], self.output)
        self.assertEqual(self.output.getvalue(), "")

    def test_only_unchanged(self):
        """Test case: only unchanged"""

        unchanged = ["a", "b", "c"]
        write_output_lines([], unchanged, self.output)
        self.assertEqual(self.output.getvalue(), "a\nb\nc\n")

    def test_only_changed_sorted_by_replaced_chars_desc(self):
        """Test case: only changed with descending sorting by replaced chars count"""

        changed = [("short", 1), ("longer", 3), ("medium", 2)]
        write_output_lines(changed, [], self.output)
        self.assertEqual(self.output.getvalue(), "longer\nmedium\nshort\n")

    def test_mixed(self):
        """Test case: changed and unchanged lines"""

        changed = [("X", 2), ("Y", 1)]
        unchanged = ["A", "B"]
        write_output_lines(changed, unchanged, self.output)
        self.assertEqual(self.output.getvalue(), "X\nY\nA\nB\n")


if __name__ == "__main__":
    unittest.main()

# Prevent unittest abstract class failings.
del BaseReplacerTest
del BaseNonOverlappingTest
