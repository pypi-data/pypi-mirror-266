from dataclasses import dataclass
from typing import Optional

from proquo.core.Reference import Reference
from proquo.core.Quote import Quote


@dataclass
class QuoteRef:
    quote: Quote
    reference: Optional[Reference]
    text: str
    pred: float = 0
