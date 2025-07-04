from collections import defaultdict
from typing import Dict, Generic, List, Optional, TypeVar, Callable

T = TypeVar("T")


class TrieNode(Generic[T]):
    def __init__(self):
        self.children: Dict[str, TrieNode[T]] = defaultdict(TrieNode)
        self.items: List[T] = []


class Trie(Generic[T]):
    def __init__(self):
        self.root = TrieNode[T]()

    def insert(self, key: str, item: T) -> None:
        """Insert a key and associate it with an item."""
        node = self.root
        for char in key:
            node = node.children[char]
        node.items.append(item)

    def search_prefix(
        self, prefix: str, predicate: Optional[Callable[[T], bool]] = None
    ) -> List[T]:
        """Return all items stored in the subtree matching the prefix."""
        node = self.root
        last_node = node
        for char in prefix:
            if char not in node.children:
                items = self._collect_all_items(last_node)
                return (
                    [item for item in items if predicate(item)] if predicate else items
                )
            node = node.children[char]
            last_node = node
        items = self._collect_all_items(node)
        return [item for item in items if predicate(item)] if predicate else items

    def _collect_all_items(self, node: TrieNode[T]) -> List[T]:
        """Recursively collect all items under the given node."""
        results = list(node.items)
        for child in node.children.values():
            results.extend(self._collect_all_items(child))
        return results
