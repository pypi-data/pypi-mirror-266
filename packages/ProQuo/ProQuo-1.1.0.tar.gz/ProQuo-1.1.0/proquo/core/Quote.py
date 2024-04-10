from dataclasses import dataclass


@dataclass
class Quote:
    start: int
    end: int
    text: str
