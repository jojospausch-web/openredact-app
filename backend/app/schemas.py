from typing import List, Dict, Any, Optional
from pydantic import BaseModel


def to_camel_case(snake_case):
    pascal_case = snake_case.title().replace("_", "")
    return pascal_case[0].lower() + pascal_case[1:]


class CamelBaseModel(BaseModel):
    # This base model automatically defines a camelCase public representation that is used by API clients.
    # Note: docstrings are automatically used as description for JSON schemas (and they are inherited)

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True


class Annotation(CamelBaseModel):
    start: int
    end: int
    tag: str


class AnnotationsForEvaluation(CamelBaseModel):
    computed_annotations: List[Annotation]
    gold_annotations: List[Annotation]


class Scores(CamelBaseModel):
    f1: float
    f2: float
    precision: float
    recall: float
    true_positives: float
    false_positives: float
    false_negatives: float


class EvaluationResponse(CamelBaseModel):
    total: Scores
    tags: Dict[str, Scores]


class Pii(CamelBaseModel):
    start_char: int
    end_char: int
    tag: str
    text: str
    score: float
    recognizer: str
    start_tok: int
    end_tok: int


class Token(CamelBaseModel):
    text: str
    has_ws: bool
    br_count: int
    start_char: int
    end_char: int


class FindPiisResponse(CamelBaseModel):
    piis: List[Pii]
    tokens: List[Token]
    format: str


class AnonymizedPii(CamelBaseModel):
    text: str
    id: str


class AnonymizedPiisResponse(CamelBaseModel):
    anonymized_piis: List[AnonymizedPii]


class ErrorMessage(BaseModel):
    detail: str


# Whitelist schemas
class WhitelistResponse(CamelBaseModel):
    """Response containing all whitelist entries"""

    entries: List[str]


class WhitelistEntry(CamelBaseModel):
    """Single whitelist entry"""

    entry: str


class WhitelistBulkUpdate(CamelBaseModel):
    """Bulk update whitelist entries"""

    entries: List[str]


# Template schemas
class TemplateData(CamelBaseModel):
    """Template data structure"""

    name: str
    description: Optional[str] = ""
    default_mechanism: Dict[str, Any]
    mechanisms_by_tag: Dict[str, Dict[str, Any]]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TemplateResponse(CamelBaseModel):
    """Single template response"""

    template_id: str
    template: TemplateData


class TemplatesResponse(CamelBaseModel):
    """Response containing all templates"""

    templates: Dict[str, TemplateData]


class TemplateImport(CamelBaseModel):
    """Import templates payload"""

    templates: Dict[str, TemplateData]


class SuccessResponse(CamelBaseModel):
    """Generic success response"""

    success: bool
    message: Optional[str] = None
