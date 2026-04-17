# Substrings replacer
Performs a character replacement in strings according to the configuration key1=value1,key2=value2,...

## Requirements
- Python >= 3.7 version (only stdlib used).


## Launch

### From console
```bash
python3 -m main datasets/config_simple.txt datasets/sample_simple.txt --method aho_corasick
```

- **config.txt** – file with key=value pairs (each pair on a new line, order determines priority).
- **sample.txt**  – file with replacement text (line-by-line processing).
- **--method** – replacement method:
    - **cascading** – cascading replacement (each key is applied to the result of the previous one). Defaults.
    - **single_pass** – single-pass search of keys for each position.
    - **regexp – single** regular expression with alternatives.
    - **aho_corasick** – Aho-Corasick algorithm (recommended for large numbers of keys).

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
            <td colspan="3">L - length of the string, K - number of keys</td>
        </tr>
    </tbody>
</table>


## Testing

```
bash
python -m unittest discover tests
```
The tests check:
- Correctness of substitution (comparison of results between modes).
- Non-overlapping and priority keys.
- Handling of empty strings, special characters, and edge cases.
- Working with the configuration file parser
- Performance benchmark and comparison results between replacers.

## Project structure

```text
main.py                   # Entry point.
parsers.py                # Config parsing.
replacers/
├── __init__.py
├── aho_corasick.py       # Aho‑Corasick algorithm.
├── cascading.py          # Cascade replacing.
├── regexp.py             # Regexp sub replacing.
├── single_pass.py        # Single-pass replacing.
├── type_defs.py          # Common types.
tests/
├── test_benchmark.py     # Benchmark comparison.
├── test_replacers.py     # Test replacers.
└── test_parsers.py       # Test parsing.
datasets/                 # Sample files.
```