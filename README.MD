# Substrings replacer
Performs a character replacement in strings according to the configuration key1=value1,key2=value2,...

## Requirements
- Python >= 3.7 version (only stdlib used).
- https://pypi.org/project/pyahocorasick (Optional, if use aho_corasick_c)

## Launch

### From console
```bash
python3 -m main datasets/config_simple.txt datasets/sample_simple.txt --method aho_corasick
```

- **config** – file with key=value pairs (each pair on a new line, order determines priority).
- **sample**  – file with replacement text (line-by-line processing).
- **--method** – replacement method:
    - **cascading** – cascading replacement (each key is applied to the result of the previous one). Defaults.
    - **single_pass** – single-pass search of keys for each position.
    - **regexp – single** regular expression with alternatives.
    - **aho_corasick** – Aho-Corasick algorithm (recommended for large numbers of keys).
    - **aho_corasick_c** – Aho-Corasick pyahocorasick (C) wrapper (the fastest implementation for large numbers of keys).

The result is output to stdout: first the lines in which substitutions occurred (sorted by descending number of substitutions), then the unchanged lines.

### From code
```Python
from replacers import AhoCorasickReplacer, Replacements

replacements = Replacements([("ab", "X"), ("bc", "Y")])
replacer = AhoCorasickReplacer(replacements)

new_line, replaced_count = replacer.apply("abc")
print(new_line)        # Xc
print(replaced_count)  # 2
```


## Algorithms
<table>
    <thead>
        <tr>
            <th>Method</th>
            <th>Complexity</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><i>cascading</i></td>
            <td><b>O(K * L)</b></td>
            <td>Sequential str.replace. May produce false replacements (cascade). Fast, but not correct for disjoint requirements.</td>
        </tr>
        <tr>
            <td><i>single_pass</i></td>
            <td><b>O(L * K)</b></td>
            <td>Enumerate all keys for each position. Correct, but slow for large K.</td>
        </tr>
        <tr>
            <td><i>regexp</i></td>
            <td><b>O(L)</b></td>
            <td>One pass using re.sub. Takes into account the order of alternatives.</td>
        </tr>
        <tr>
            <td><i>aho_corasick</i></td>
            <td><b>O(L + M)</b></td>
            <td>Building of an automaton (M is the total length of keys) and linear search. Optimal for a large number of keys.</td>
        </tr>
        <tr>
            <td><i>aho_corasick_с</i></td>
            <td><b>O(L + M)</b></td>
            <td>AhoCorasick C wrapper (https://pypi.org/project/pyahocorasick). Optimal for a large number of keys.</td>
        </tr>
        <tr>
            <td colspan="3"><b>L</b> - length of the string, <b>K</b> - number of keys</td>
        </tr>
    </tbody>
</table>


## Testing

Make datasets:
```bash
python3 -m tests.make_datasets datasets/config.txt datasets/sample.txt --total_pairs 1000 --total_lines 1000
```

Launch all tests:
```bash
python3 -m unittest discover tests
```
The tests check:
- Correctness of substitution (comparison of results between modes).
- Non-overlapping and priority keys.
- Handling of empty strings, special characters, and edge cases.
- Working with the configuration file parser
- Performance benchmark and comparison results between replacers.


## Performance
<table>
    <caption>
        <b>1000 lines and 1000 replacements pairs</b>
    </caption>
    <thead>
        <tr>
            <td>Replacer</d>
            <td>Time (s)</d>
            <td>Ratio(x)</d>
            <td>Replaced chars</d>
            <td>Replacements length</d>
            <td>Text length</d>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>aho_corasick_c</td>
            <td>0.004124</td>
            <td>x1.00</td>
            <td>4891</td>
            <td>1000</td>
            <td>1000</td>
        </tr>
        <tr>
            <td>aho_corasick</td>
            <td>0.017762</td>
            <td>x4.31</td>
            <td>4891</td>
            <td>1000</td>
            <td>1000</td>
        </tr>
        <tr>
            <td>cascading</td>
            <td>0.112779</td>
            <td>x27.35</td>
            <td>4885</td>
            <td>1000</td>
            <td>1000</td>
        </tr>
        <tr>
            <td>regexp</td>
            <td>0.229525</td>
            <td>x55.66</td>
            <td>4891</td>
            <td>1000</td>
            <td>1000</td>
        </tr>
        <tr>
            <td>single_pass</td>
            <td>6.491263</td>
            <td>x1574.18</td>
            <td>4891</td>
            <td>1000</td>
            <td>1000</td>
        </tr>
    </tbody>
<table>


## Project structure

```text
main.py                   # Entry point.
parsers.py                # Config parsing.
replacers/
├── __init__.py
├── aho_corasick.py       # Aho‑Corasick algorithms.
├── cascading.py          # Cascade replacing.
├── regexp.py             # Regexp sub replacing.
├── single_pass.py        # Single-pass replacing.
├── type_defs.py          # Common types.
tests/
├── make_datasets.py      # Make datasets files.
├── test_benchmark.py     # Benchmark comparison.
├── test_parsers.py       # Test parsing.
└── test_replacers.py     # Test replacers.
datasets/                 # Sample files.
```