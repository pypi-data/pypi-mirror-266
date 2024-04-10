from dataclasses import dataclass
from quid.match.Match import Match
from proquo.core import Reference


@dataclass
class MatchRef(Match):
    reference: Reference

    def __init__(self, source_span, target_span, reference: Reference = None):
        super().__init__(source_span, target_span)
        self.reference = reference

    @classmethod
    def from_match(cls, match: Match):
        return cls(match.source_span, match.target_span)
