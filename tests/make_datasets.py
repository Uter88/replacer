import random
import string
from typing import OrderedDict, List
import argparse
from pathlib import Path


def generate_replacements_config(
    file_path: Path, total_pairs: int = 1000
) -> OrderedDict[str, str]:
    """Generate replacements config and write it to destination file.

    Args:
        file_path (str): Destination file path.
        total_pairs (Optional[int]): Number of pairs. Defaults to 1000.

    Returns:
        OrderedDict[str, str]: Replacement pairs.
    """

    replacements: OrderedDict[str, str] = OrderedDict()
    exits_keys = set()

    with open(file_path, "w", encoding="utf-8") as f:
        for _ in range(total_pairs):
            while True:
                random_key_length = random.randint(3, 10)

                key = "".join(
                    random.choices(
                        string.ascii_lowercase + string.digits, k=random_key_length
                    )
                )

                if key not in exits_keys:
                    exits_keys.add(key)
                    break

            value_length = random.randint(2, 5)
            value = "".join(random.choices(string.ascii_lowercase, k=value_length))

            f.write(f"{key}={value}\n")
            replacements[key] = value

    print(f"Generated {total_pairs} pairs in {file_path}")
    return replacements


def generate_sample_lines(
    file_path: Path,
    replacements: OrderedDict[str, str],
    total_lines: int = 1000,
    avg_line_length: int = 80,
    probability: float = 0.1,
):
    """Generate sample lines and write it to destination file.
    Use replacements keys for random selection and define weights for choices.
    If random() les than probability - select random key, otherwise select random character.

    Args:
        file_path (str): Destination file path.
        replacements (OrderedDict[str, str]): Replacements pairs.
        total_lines (Optional[int]): Total number of lines. Defaults to 1000.
        avg_line_length (Optional[int]): Average line length. Defaults to 80.
        probability (Optional[float]): Probability of selection character from replacements keys. Defaults to 0.1.

    Raises:
        ValueError: If empty replacements.
    """

    keys = list(replacements.keys())

    if not keys:
        raise ValueError("Empty replacements")

    key_weights = [len(k) for k in keys]

    with open(file_path, "w", encoding="utf-8") as f:
        for _ in range(total_lines):
            line_characters: List[str] = []
            position = 0
            target_len = random.randint(avg_line_length // 2, avg_line_length * 2)

            while position < target_len:
                if random.random() < probability:
                    key = random.choices(keys, weights=key_weights, k=1)[0]
                    line_characters.append(key)
                    position += len(key)
                else:
                    character = random.choice(
                        string.ascii_letters + string.digits + " .,!?;:-"
                    )
                    line_characters.append(character)
                    position += 1

            line = "".join(line_characters)[:target_len]

            f.write(line + "\n")

    print(f"Generated {total_lines} lines in {file_path}")


def main():
    parser = argparse.ArgumentParser(description="Replacer")
    parser.add_argument("config", help="Destination config file path", type=Path)
    parser.add_argument("sample", help="Destination sample file path", type=Path)
    parser.add_argument(
        "--total_pairs", help="Total replacement pairs", default=1000, type=int
    )

    parser.add_argument(
        "--total_lines", help="Total text lines", default=1000, type=int
    )

    args = parser.parse_args()
    config_file: Path = args.config
    sample_file: Path = args.sample
    total_pairs: int = args.total_pairs
    total_lines: int = args.total_lines

    print("Start generating replacements config file..")
    replacements = generate_replacements_config(config_file, total_pairs)

    print("Start generating sample file...")
    generate_sample_lines(
        sample_file, replacements, total_lines, avg_line_length=80, probability=0.12
    )

    print("Ready!")


if __name__ == "__main__":
    main()
