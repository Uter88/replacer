from collections import deque
from typing import Dict, Optional, Deque, List, Tuple

from .type_defs import Replacements, ReplaceResult


class Node:
    """
    Aho-Corasick trie node.

    Attributes:
        children (Dict[str, Node]): Dictionary of symbol transitions.
        fail_link: (Optional[Node]): Suffix link to the longest proper suffix.
        output_len (int): Best key length which ending at this node or its suffix.
        output_priority (int): Priority index (lower = higher priority).
        output_value (Optional[str]): Replacement string.
    """

    __slots__ = (
        "children",
        "fail_link",
        "output_len",
        "output_priority",
        "output_value",
    )
    children: Dict[str, "Node"]
    fail_link: Optional["Node"]
    output_len: int
    output_priority: int
    output_value: Optional[str]

    def __init__(self):
        self.children = {}
        self.fail_link = None
        self.output_len = 0
        self.output_priority = -1
        self.output_value = None


class AhoCorasickReplacer:
    """Aho-Corasick replacement algorithm implementation.

    Links:
        https://en.wikipedia.org/wiki/Aho-Corasick_algorithm.
        https://pypi.org/project/pyahocorasick
    """

    def __init__(self, replacements: Replacements):
        self.root = Node()
        self._build(replacements)

    def _build(self, replacements: Replacements) -> None:
        """Start building trie.

        Complexity:
            O(N) where N = summary length of all keys.

        Args:
            replacements (Replacements): Replacements pairs.
        """

        queue = self._build_trie_and_init_queue(replacements)
        self._build_tree(queue)

    def _build_trie_and_init_queue(self, replacements: Replacements) -> Deque[Node]:
        """Inserting keys into the trie.

        - Each key iterates through the symbols, creating new nodes if necessary.
        - The terminal node stores the key length, its priority, and the replacement value.
        - If node was already a terminal for another key, the one with the higher priority is retained.
        - For all children of the root, fail is set to the root and put them to queue.

        Args:
            replacements (Replacements): Replacements pairs.

        Returns:
            Deque[Node]: Queue with nodes for BFS.
        """

        for priority, (key, value) in enumerate(replacements.items()):
            node = self.root

            for ch in key:
                if ch not in node.children:
                    node.children[ch] = Node()

                node = node.children[ch]

            is_higher_priority = (
                node.output_priority == -1 or priority < node.output_priority
            )

            if is_higher_priority:
                node.output_len = len(key)
                node.output_priority = priority
                node.output_value = value

        queue: Deque[Node] = deque()

        for child in self.root.children.values():
            child.fail_link = self.root
            queue.append(child)

        return queue

    def _build_tree(self, queue: Deque[Node]) -> None:
        """Building fail links and distribution outputs.

        - If its fail node has an output, and this output has a higher priority than the current output,
        then we copy the output from the fail node to the current node.
        This ensures that each node stores the best key among all suffixes.

        - For each child, we calculate the fail link for the character ch:
        We follow the fail links from current.fail until we find a node that has a transition on ch.
        If such a node is found, child.fail = f.children[ch]; otherwise, child.fail = self.root.

        - Add child to the queue for further processing.

        Args:
            queue (Deque[Node]): Queue with nodes.
        """

        while queue:
            current = queue.popleft()

            if current.fail_link and current.fail_link.output_len > 0:
                is_best_node = (
                    current.output_priority == -1
                    or current.fail_link.output_priority < current.output_priority
                )

                if is_best_node:
                    current.output_len = current.fail_link.output_len
                    current.output_priority = current.fail_link.output_priority
                    current.output_value = current.fail_link.output_value

            for ch, child in current.children.items():
                f = current.fail_link

                while f is not None and ch not in f.children:
                    f = f.fail_link

                child.fail_link = self.root if f is None else f.children[ch]
                queue.append(child)

    def _gather_matches(self, line: str) -> List[Tuple[int, int, int, str]]:
        """Gather matches.

        Complexity:
            O(N * L): were N = len(line), L = max trie deep.

        - Iterate through the string character by character,
        moving through the automaton (using fail links when there is no transition).

        - At each position i, we traverse the fail chain from the current state and add all keys
        that end at that position (including those accessible via fail links).
        Each key is remembered with its start, end, priority, and value.

        Args:
            line (str): Line to search matches.

        Returns:
            List[Tuple[int, int, int, str]]: Start, end, priority, value.
        """

        matches = []
        state = self.root

        for i, ch in enumerate(line):
            while state != self.root and ch not in state.children:
                state = state.fail_link if state.fail_link is not None else self.root

            if ch in state.children:
                state = state.children[ch]
            else:
                state = self.root

            if state.output_len > 0 and state.output_value is not None:
                start = i - state.output_len + 1
                matches.append((start, i, state.output_priority, state.output_value))

        return matches

    def _select_matches(
        self, line: str, matches: List[Tuple[int, int, int, str]]
    ) -> ReplaceResult:
        """Selecting non-overlapping matches based on priority.

        Complexity:
            O(K log K + N): where K = len(line), N = len(matches)

        - Sort all found matches by their starting position,
        and if they have the same starting position - by priority.

        - Iterate through the sorted list and add to the result
        only those matches that do not intersect with the previously selected one.
        This ensures that the best non-intersecting key is selected at each position.

        Args:
            line (str): Line to replace.
            matches (List[Tuple[int, int, int, str]]): Matches lines.

        Returns:
            ReplaceResult: Replaced line and replacing count.
        """

        matches.sort(key=lambda x: (x[0], x[2]))

        result_parts = []
        replaced_chars = 0
        last_end = -1

        for start, end, _, value in matches:
            if start > last_end:
                if last_end + 1 <= start - 1:
                    result_parts.append(line[last_end + 1 : start])

                result_parts.append(value)
                replaced_chars += end - start + 1
                last_end = end

        result_parts.append(line[last_end + 1 :])

        return "".join(result_parts), replaced_chars

    def apply(self, line: str) -> ReplaceResult:
        """Replaces all non-overlap keys to values.

        Args:
            line (str): Line to replace.

        Returns:
            ReplaceResult: Replaced line and replacing count.
        """

        if not line:
            return "", 0

        matches = self._gather_matches(line)
        replaced_line, replaced_chars = self._select_matches(line, matches)

        return replaced_line, replaced_chars

    def __call__(self, line: str, _: Replacements) -> ReplaceResult:
        """Call apply replacing"""

        return self.apply(line)
