from dataclasses import dataclass


@dataclass
class Reference:
    start: int
    end: int
    text: str
    page: int
