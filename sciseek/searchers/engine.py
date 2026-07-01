"""Search engines used by SciSeek service."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from sciseek.core.exceptions import ValidationError
from sciseek.core.models import Occurrence, SearchMode

from .boolean_parser import BooleanParser, evaluate


@dataclass(slots=True)
class SearchOutput:
    matched_terms: List[str]
    occurrences: List[Occurrence]

    @property
    def match_count(self) -> int:
        return sum(o.count for o in self.occurrences)


class SearchEngine:
    def __init__(self, case_sensitive: bool = False, proximity_words: int = 10, context_words: int = 20):
        self.case_sensitive = case_sensitive
        self.proximity_words = proximity_words
        self.context_words = context_words

    def validate_regex_terms(self, terms: List[str]) -> None:
        for pattern in terms:
            try:
                re.compile(pattern)
            except re.error as exc:
                raise ValidationError(f"Regex invalida: {pattern} ({exc})") from exc

    def search(self, mode: SearchMode, text: str, terms: List[str], boolean_query: str = "") -> SearchOutput:
        if mode == SearchMode.SIMPLE:
            return self._search_simple(text, terms)
        if mode == SearchMode.REGEX:
            return self._search_regex(text, terms)
        if mode == SearchMode.PROXIMITY:
            return self._search_proximity(text, terms)
        if mode == SearchMode.BOOLEAN:
            return self._search_boolean(text, boolean_query)
        raise ValidationError("Modo de busca desconhecido.")

    def _search_simple(self, text: str, terms: List[str]) -> SearchOutput:
        source = text if self.case_sensitive else text.lower()
        occ: List[Occurrence] = []
        matched: List[str] = []
        for term in terms:
            token = term if self.case_sensitive else term.lower()
            count = source.count(token)
            if count > 0:
                matched.append(term)
                occ.append(Occurrence(term=term, count=count, snippet=self._snippet(text, token)))
        return SearchOutput(matched_terms=matched, occurrences=occ)

    def _search_regex(self, text: str, terms: List[str]) -> SearchOutput:
        flags = 0 if self.case_sensitive else re.IGNORECASE
        occ: List[Occurrence] = []
        matched: List[str] = []
        for pattern in terms:
            regex = re.compile(pattern, flags)
            hits = list(regex.finditer(text))
            if hits:
                matched.append(pattern)
                snippet = self._snippet(text, hits[0].group(0))
                occ.append(Occurrence(term=pattern, count=len(hits), snippet=snippet))
        return SearchOutput(matched_terms=matched, occurrences=occ)

    def _search_proximity(self, text: str, terms: List[str]) -> SearchOutput:
        if len(terms) < 2:
            raise ValidationError("Busca por proximidade requer ao menos 2 termos.")
        source = text if self.case_sensitive else text.lower()
        words = source.split()
        matched: List[str] = []
        occ: List[Occurrence] = []
        pairs = zip(terms[:-1], terms[1:], strict=False)
        for t1, t2 in pairs:
            token1 = t1 if self.case_sensitive else t1.lower()
            token2 = t2 if self.case_sensitive else t2.lower()
            idx1 = [i for i, w in enumerate(words) if token1 in w]
            idx2 = [i for i, w in enumerate(words) if token2 in w]
            near = 0
            for i in idx1:
                for j in idx2:
                    if abs(i - j) <= self.proximity_words:
                        near += 1
            if near > 0:
                matched.extend([t1, t2])
                occ.append(Occurrence(term=f"{t1}~{t2}", count=near, snippet=self._snippet(text, token1)))
        unique = sorted(set(matched), key=lambda x: x.lower())
        return SearchOutput(matched_terms=unique, occurrences=occ)

    def _search_boolean(self, text: str, boolean_query: str) -> SearchOutput:
        if not boolean_query.strip():
            raise ValidationError("Expressao booleana vazia.")
        tree = BooleanParser(boolean_query).parse()
        ok = evaluate(tree, text, self.case_sensitive)
        if not ok:
            return SearchOutput(matched_terms=[], occurrences=[])
        terms = [t for t in re.findall(r"[^\s()]+", boolean_query) if t.upper() not in {"AND", "OR", "NOT"}]
        unique_terms = sorted(set(terms), key=lambda x: x.lower())
        occ = [Occurrence(term=t, count=1, snippet=self._snippet(text, t if self.case_sensitive else t.lower())) for t in unique_terms]
        return SearchOutput(matched_terms=unique_terms, occurrences=occ)

    def _snippet(self, text: str, needle: str) -> str:
        hay = text if self.case_sensitive else text.lower()
        idx = hay.find(needle)
        if idx < 0:
            return ""
        start = max(0, idx - 120)
        end = min(len(text), idx + len(needle) + 120)
        return text[start:end].replace("\n", " ").strip()

