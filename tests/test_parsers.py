import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch


from replacers.type_defs import ReplaceMethod
from parsers import (
    ConfigLineParseError,
    _parse_config_line,
    parse_replacements,
    parse_command_line_args,
    parse_file_exception,
)


class TestParseConfigLine(unittest.TestCase):
    """Testing _parse_config_line"""

    def test_valid_line(self):
        """Testing valid line format"""

        self.assertEqual(_parse_config_line("key=value"), ("key", "value"))
        self.assertEqual(_parse_config_line("  key  =  value  "), ("key", "value"))
        self.assertEqual(_parse_config_line("a=b=c"), ("a", "b=c"))

    def test_invalid_line(self):
        """Test case: invalid line format"""

        with self.assertRaises(ConfigLineParseError) as ctx:
            _parse_config_line("key value")

        self.assertIn("expected 'key=value' format", str(ctx.exception))

    def test_empty_key(self):
        """Test case: line with empty key"""

        with self.assertRaises(ConfigLineParseError) as ctx:
            _parse_config_line("=value")

        self.assertIn("key is empty", str(ctx.exception))

        with self.assertRaises(ConfigLineParseError):
            _parse_config_line("  =value")

    def test_empty_value(self):
        """Test case: line with empty value"""

        with self.assertRaises(ConfigLineParseError) as ctx:
            _parse_config_line("key=")

        self.assertIn("value is empty", str(ctx.exception))

        with self.assertRaises(ConfigLineParseError):
            _parse_config_line("key=  ")

    def test_key_equals_value(self):
        """Test case: equals key and value"""

        with self.assertRaises(ConfigLineParseError) as ctx:
            _parse_config_line("same=same")

        self.assertIn("key and value are the same", str(ctx.exception))

        with self.assertRaises(ConfigLineParseError):
            _parse_config_line("  same  =  same  ")


class TestParseReplacements(unittest.TestCase):
    """Testing parse_replacements"""

    def setUp(self):
        self.patcher = patch("sys.stderr", new_callable=StringIO)
        self.mock_stderr = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_empty_lines_ignored(self):
        """Test case: ignoring empty lines"""

        lines = ["", "   ", "a=b", "", "c=d"]
        result = parse_replacements(lines)
        self.assertEqual(result, {"a": "b", "c": "d"})
        self.assertEqual(self.mock_stderr.getvalue(), "")

    def test_invalid_lines_ignored_with_errors(self):
        """Test case: ignoring invalid lines with errors"""

        lines = ["a=b", "invalid", "c=d", "x="]
        result = parse_replacements(lines)
        self.assertEqual(result, {"a": "b", "c": "d"})
        err_output = self.mock_stderr.getvalue()
        self.assertIn("Line 2: expected 'key=value' format", err_output)
        self.assertIn("Line 4: value is empty", err_output)

    def test_empty_lines(self):
        """Test case: empty lines"""

        lines = []
        result = parse_replacements(lines)
        self.assertEqual(result, {})
        err_output = self.mock_stderr.getvalue()
        self.assertIn("No valid key=value pairs found", err_output)

    def test_duplicate_keys_last_wins(self):
        """Test case: deduplicate keys with last key wins"""

        lines = ["a=1", "b=2", "a=3"]
        result = parse_replacements(lines)
        self.assertEqual(result, {"a": "3", "b": "2"})

    def test_keeps_ordering(self):
        """Test case: keep keys ordering"""

        lines = ["x=a", "y=b", "z=c"]
        result = parse_replacements(lines)
        self.assertEqual(result, {"x": "a", "y": "b", "z": "c"})


class TestParseCommandLineArgs(unittest.TestCase):
    """Testing parse_command_line_args"""

    def setUp(self):
        self.patcher_args = patch("sys.argv", ["replacer.py"])
        self.mock_args = self.patcher_args.start()

    def tearDown(self):
        self.patcher_args.stop()

    def test_minimal_args(self):
        """Test case: minimum args received"""

        with patch("sys.argv", ["replacer.py", "config.txt", "sample.txt"]):
            config, sample, method = parse_command_line_args()
            self.assertEqual(config, Path("config.txt"))
            self.assertEqual(sample, Path("sample.txt"))
            self.assertEqual(method, ReplaceMethod.CASCADING)

    def test_valid_method_arg(self):
        """Test case: valid method arg"""

        with patch("sys.argv", ["replacer.py", "cfg", "smp", "--method", "cascading"]):
            _, _, method = parse_command_line_args()
            self.assertEqual(method, ReplaceMethod.CASCADING)

    def test_invalid_method_arg(self):
        """Test case: invalid method arg"""

        with patch("sys.argv", ["replacer.py", "cfg", "smp", "--method", "invalid"]):
            with patch("sys.stderr", new_callable=StringIO):
                with self.assertRaises(SystemExit):
                    parse_command_line_args()

    def test_config_sample_same_file(self):
        """Test case: same config and sample files"""

        with patch("sys.argv", ["replacer.py", "same.txt", "same.txt"]):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                with self.assertRaises(SystemExit):
                    parse_command_line_args()
                self.assertIn(
                    "Config and sample files must be different", mock_stderr.getvalue()
                )


class TestParseFileException(unittest.TestCase):
    """Testing parse_file_exception"""

    def test_file_not_found_error(self):
        """Test case: FileNotFoundError exception"""

        e = FileNotFoundError("No such file", "missing.txt")
        e.filename = "missing.txt"
        result = parse_file_exception(e)
        self.assertEqual(result, "file not found: missing.txt")

    def test_permission_error(self):
        """Test case: PermissionError exception"""

        e = PermissionError("Permission denied", "forbidden.txt")
        e.filename = "forbidden.txt"
        result = parse_file_exception(e)
        self.assertEqual(result, "permission denied: forbidden.txt")

    def test_is_a_directory_error(self):
        """Test case: IsADirectoryError exception"""

        e = IsADirectoryError("Is a directory", "my_dir")
        e.filename = "my_dir"
        result = parse_file_exception(e)
        self.assertEqual(result, "expected file, found directory: my_dir")

    def test_oserror_without(self):
        """Test case: OSError exception"""

        e = OSError("Some error")
        e.errno = 13
        e.strerror = "Some error"
        result = parse_file_exception(e)
        self.assertEqual(result, "I/O error (13): Some error")

    def test_unicode_decode_error(self):
        """Test case: UnicodeDecodeError exception"""

        try:
            b"\xff".decode()
        except UnicodeDecodeError as e:
            result = parse_file_exception(e)
            self.assertIn("decoding error at position", result)
            self.assertIn("file is not UTF-8 encoded", result)
        else:
            self.fail("UnicodeDecodeError not raised")

    def test_unexpected_error(self):
        """Test case: unexpected exception"""

        e = ValueError("something wrong")
        result = parse_file_exception(e)
        self.assertEqual(result, "unexpected error: something wrong")


if __name__ == "__main__":
    unittest.main()
