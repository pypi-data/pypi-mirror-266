from enum import Enum

class ModeEnum(str, Enum):
    fingerprint = "fingerprint",
    keyword = "keyword",
    hybrid = "hybrid",
    document = "document",
    document_fingerprint = "document_fingerprint",
    fingerprint_keyword = "fingerprint_keyword",
    auto = "auto",
    
    def __str__(self) -> str:
        return self.value
