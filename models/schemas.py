from pydantic import BaseModel


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
