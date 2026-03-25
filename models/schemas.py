from typing import Literal, Optional

from pydantic import BaseModel, field_validator, model_validator


# ── LLM output schema ─────────────────────────────────────────────────

class PageReasoning(BaseModel):
    page: int
    matched_patterns: list[str]

    @field_validator("matched_patterns")
    @classmethod
    def patterns_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("matched_patterns must not be empty for a classified page")
        return v


class DocumentResult(BaseModel):
    document_type: str
    page_numbers: list[int]
    reasoning: list[PageReasoning]


class LLMMetadata(BaseModel):
    file_id: str
    pdf_name: str
    time_taken_to_process: float  # seconds from PDF received → final output


class LLMOutput(BaseModel):
    documents: list[DocumentResult]
    status: Optional[Literal["pass", "fail"]] = None
    cost: Optional[float] = None
    reason: Optional[str] = None
    metadata: Optional[LLMMetadata] = None
    optional_data: Optional[dict[str, list[str]]] = None

    @model_validator(mode="after")
    def documents_not_empty(self) -> "LLMOutput":
        if not self.documents:
            raise ValueError("documents list must not be empty")
        return self


# ── API request / response schemas ────────────────────────────────────

class PageIn(BaseModel):
    page_number: int
    text: str


class ClientMetaData(BaseModel):
    loan_client: str
    loan_state: str
    county: str
    loan_type: str


class ClassifyRequest(BaseModel):
    pages: list[PageIn]
    total_pages: int
    environment: str
    checksum: str
    raw_pdf_path: str
    file_id: int
    client_meta_data: ClientMetaData


class ClassifyResponse(BaseModel):
    file_id: int
    pdf_name: str
    total_pages: int
    pred_summons_pages: list[int]
    pred_complaint_pages: list[int]
    pred_summons_count: int
    pred_complaint_count: int
    top10_summons_pages: list[int]
    top10_complaint_pages: list[int]
