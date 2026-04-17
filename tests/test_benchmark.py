import timeit
import statistics
import unittest
from typing import Tuple, List, Dict, Callable

from parsers import parse_replacements

from replacers import (
    cascading_replacer,
    single_pass_replacer,
    RegexpReplacer,
    AhoCorasickReplacer,
    AhoCorasickReplacerC,
    Replacements,
    Replacer,
    ReplaceMethod,
)


class BenchmarkReplacers(unittest.TestCase):
    simple_replacements: Replacements
    many_keys_replacements: Replacements
    overlap_replacements: Replacements
    large_replacements: Replacements

    simple_text: List[str]
    many_keys_text: List[str]
    no_match_text: List[str]
    overlap_text: List[str]
    large_text: List[str]

    @classmethod
    def setUpClass(cls):
        """Init datasets"""

        cls.simple_replacements = Replacements(
            [
                ("ab", "X"),
                ("bc", "Y"),
                ("cd", "Z"),
            ]
        )
        cls.simple_text = ["abcd" for _ in range(1000)]
        cls.many_keys_replacements = Replacements()

        for i in range(100):
            cls.many_keys_replacements[f"key{i}"] = f"val{i}"

        cls.many_keys_text = [f"key{i} " * 5 for i in range(100)]
        cls.no_match_text = ["xyz " for _ in range(10000)]

        cls.overlap_replacements = Replacements(
            [
                ("a", "Z"),
                ("ab", "X"),
                ("abc", "W"),
            ]
        )
        cls.overlap_text = ["abc" for _ in range(500)]

        with open("datasets/config_large.txt") as config_file:
            cls.large_replacements = parse_replacements(config_file)

        with open("datasets/sample_large.txt") as sample_file:
            cls.large_text = sample_file.readlines()

    def _time_it(self, func: Callable, iterations: int) -> Tuple[float, float]:
        """Time benchmark.

        Args:
            func (Callable): Function to call.
            iterations (int): Number of call iterations.

        Returns:
            Tuple[float, float]: Average and stdev time.
        """

        timer = timeit.Timer(func)
        times = timer.repeat(repeat=iterations, number=1)
        avg_time = statistics.mean(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0.0

        return avg_time, std_time

    @staticmethod
    def _get_replacers(replacements: Replacements):
        """Init replacers"""

        return (
            (ReplaceMethod.AHO_CORASICK, AhoCorasickReplacer(replacements)),
            (ReplaceMethod.AHO_CORASICK_C, AhoCorasickReplacerC(replacements)),
            (ReplaceMethod.REGEXP, RegexpReplacer(replacements)),
            (ReplaceMethod.SINGLE_PASS, single_pass_replacer),
            (ReplaceMethod.CASCADING, cascading_replacer),
            (ReplaceMethod.SINGLE_PASS, single_pass_replacer),
        )

    def _benchmark_replacer(
        self,
        replacer: Replacer,
        lines: List[str],
        replacements: Replacements,
        iterations: int = 10,
    ) -> Tuple[float, float, int]:
        """Launch replacer benchmark.

        Args:
            replacer (Replacer): Replacer to benchmark.
            lines (List[str]): Lines to replace.
            replacements (Replacements): Replacements pairs.
            iterations (int, optional): Number of iterations. Defaults to 10.

        Returns:
            Tuple[float, float, int]: Average/stdev time and number of replaced characters.
        """

        def func():
            replaced_chars = 0

            for line in lines:
                (_, count) = replacer(line, replacements)
                replaced_chars += count

            return replaced_chars

        replaced_chars = func()
        avg_time, std_time = self._time_it(func, iterations)

        return avg_time, std_time, replaced_chars

    def _print_table_header(self, test_name: str):
        """Print table header"""

        print("\n" + "=" * 80)
        print(" " * 25 + test_name)
        print(
            f"{'Replacer':<20} {'Time (s)':<12} {'Std (s)':<12} {'Replaced chars':<15} {'Text length':<12}"
        )
        print("-" * 80)

    def _print_row(
        self, name: str, avg: float, std: float, replaced: int, text_len: int
    ):
        """Print row with results"""
        print(f"{name:<20} {avg:<12.6f} {std:<12.6f} {replaced:<15} {text_len:<12}")

    def test_benchmark_simple(self):
        """Benchmark case: simple datasets"""

        self._print_table_header("SIMPLE")

        replacers = self._get_replacers(self.simple_replacements)

        for name, replacer in replacers:
            avg, std, replaced = self._benchmark_replacer(
                replacer,
                self.simple_text,
                self.simple_replacements,
                iterations=20,
            )
            self._print_row(name.value, avg, std, replaced, len(self.simple_text))

    def test_benchmark_many_keys(self):
        """Benchmark case: dataset with many keys"""

        self._print_table_header("MANY KEYS")
        replacers = self._get_replacers(self.many_keys_replacements)

        for name, replacer in replacers:
            avg, std, replaced = self._benchmark_replacer(
                replacer,
                self.many_keys_text,
                self.many_keys_replacements,
                iterations=10,
            )

            self._print_row(name.value, avg, std, replaced, len(self.many_keys_text))

    def test_benchmark_no_match(self):
        """Benchmark case: no-matching"""

        self._print_table_header("NO MATCH")
        replacements = Replacements([("ab", "X")])
        replacers = self._get_replacers(replacements)

        for name, replacer in replacers:
            avg, std, replaced = self._benchmark_replacer(
                replacer, self.no_match_text, replacements, iterations=10
            )

            self._print_row(
                name.value,
                avg,
                std,
                replaced,
                len(
                    self.no_match_text,
                ),
            )

    def test_benchmark_overlap_priority(self):
        """Benchmark case: overlap with priority"""

        self._print_table_header("OVERLAP PRIORITY")
        replacers = self._get_replacers(self.overlap_replacements)

        for name, replacer in replacers:
            avg, std, replaced = self._benchmark_replacer(
                replacer,
                self.overlap_text,
                self.overlap_replacements,
                iterations=10,
            )

            self._print_row(name.value, avg, std, replaced, len(self.overlap_text))

    def test_speed_comparison_summary(self):
        """Benchmark case: summary comparison of replacers"""

        print("\n" + "=" * 80)
        print(" " * 30 + "SUMMARY SPEED COMPARISON")
        print(
            f"{'Replacer':<15} {'Time (s)':<12} {'Ratio(x)':<15} {'Replaced chars':<15} {'Replacements length':<12}  {'Text length':<12}"
        )
        print("-" * 80)

        test_cases = (
            (
                "simple",
                self.simple_replacements,
                self.simple_text,
                self._get_replacers(
                    self.simple_replacements,
                ),
            ),
            (
                "many_keys",
                self.many_keys_replacements,
                self.many_keys_text,
                self._get_replacers(
                    self.many_keys_replacements,
                ),
            ),
            (
                "no_match",
                Replacements([("ab", "X")]),
                self.no_match_text,
                self._get_replacers(Replacements([("ab", "X")])),
            ),
            (
                "overlap",
                self.overlap_replacements,
                self.overlap_text,
                self._get_replacers(self.overlap_replacements),
            ),
            (
                "large",
                self.large_replacements,
                self.large_text,
                self._get_replacers(self.large_replacements),
            ),
        )

        for case_name, replacements, text, replacers in test_cases:
            times: Dict[str, float] = {}
            replacing: Dict[str, int] = {}

            for name, replacer in replacers:
                avg, _, replaced = self._benchmark_replacer(
                    replacer, text, replacements, iterations=5
                )

                times[name.value] = avg
                replacing[name.value] = replaced

            min_time = min(times.values())
            text_len = len(text)
            replacements_len = len(replacements)

            print(f"\n{case_name.upper()}:")

            for name in sorted(times, key=lambda k: times[k]):
                t = times[name]
                ratio = t / min_time
                print(
                    f"  {name:<15} {t:<12.6f} x{ratio:<-12.2f} {replacing[name]:<15} {replacements_len:<12} {text_len:<12}"
                )


if __name__ == "__main__":
    unittest.main()
