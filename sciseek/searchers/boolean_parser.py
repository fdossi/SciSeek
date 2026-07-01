"""Boolean query parser with AND/OR/NOT and parentheses."""

from __future__ import annotations

import re
from dataclasses import dataclass

from sciseek.core.exceptions import SearchSyntaxError

TOKEN_RE = re.compile(r"\(|\)|\bAND\b|\bOR\b|\bNOT\b|[^\s()]+", re.IGNORECASE)


@dataclass(slots=True)
class Node:
    kind: str
    value: str = ""
    left: "Node | None" = None
    right: "Node | None" = None


class BooleanParser:
    def __init__(self, text: str):
        self.tokens = [t for t in TOKEN_RE.findall(text) if t.strip()]
        self.pos = 0
        if not self.tokens:
            raise SearchSyntaxError("Expressao booleana vazia.")

    def parse(self) -> Node:
        node = self._parse_or()
        if self.pos != len(self.tokens):
            raise SearchSyntaxError("Tokens extras apos fim da expressao booleana.")
        return node

    def _peek(self) -> str | None:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def _consume(self) -> str:
        tok = self._peek()
        if tok is None:
            raise SearchSyntaxError("Fim inesperado da expressao booleana.")
        self.pos += 1
        return tok

    def _accept(self, keyword: str) -> bool:
        tok = self._peek()
        if tok is not None and tok.upper() == keyword:
            self.pos += 1
            return True
        return False

    def _parse_or(self) -> Node:
        left = self._parse_and()
        while self._accept("OR"):
            right = self._parse_and()
            left = Node(kind="OR", left=left, right=right)
        return left

    def _parse_and(self) -> Node:
        left = self._parse_unary()
        while self._accept("AND"):
            right = self._parse_unary()
            left = Node(kind="AND", left=left, right=right)
        return left

    def _parse_unary(self) -> Node:
        if self._accept("NOT"):
            child = self._parse_unary()
            return Node(kind="NOT", left=child)
        return self._parse_primary()

    def _parse_primary(self) -> Node:
        tok = self._consume()
        if tok == "(":
            node = self._parse_or()
            if self._consume() != ")":
                raise SearchSyntaxError("Parenteses desbalanceados na expressao booleana.")
            return node
        if tok == ")":
            raise SearchSyntaxError("Parenteses desbalanceados na expressao booleana.")
        upper = tok.upper()
        if upper in {"AND", "OR", "NOT"}:
            raise SearchSyntaxError(f"Operador inesperado: {tok}")
        return Node(kind="TERM", value=tok)


def evaluate(node: Node, text: str, case_sensitive: bool = False) -> bool:
    source = text if case_sensitive else text.lower()

    def has_term(term: str) -> bool:
        token = term if case_sensitive else term.lower()
        return token in source

    if node.kind == "TERM":
        return has_term(node.value)
    if node.kind == "NOT":
        if node.left is None:
            return False
        return not evaluate(node.left, text, case_sensitive)
    if node.kind == "AND":
        if node.left is None or node.right is None:
            return False
        return evaluate(node.left, text, case_sensitive) and evaluate(node.right, text, case_sensitive)
    if node.kind == "OR":
        if node.left is None or node.right is None:
            return False
        return evaluate(node.left, text, case_sensitive) or evaluate(node.right, text, case_sensitive)
    return False
