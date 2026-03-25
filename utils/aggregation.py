"""
Build API responses from raw per-page inference results.
"""
from __future__ import annotations

from config import DEFAULT_COST, DEFAULT_REASON, DEFAULT_STATUS

TOP_K = 10

_LABEL_TO_DOC_TYPE = {
    "SUMMONS":   "Summons",
    "COMPLAINT": "Complaint and State of Claim",
    "OTHER":     "Other",
}


def build_llm_response(
    file_id: int | str,
    pdf_name: str,
    results: list[dict],
    time_taken: float = 0.0,
) -> dict:
    """
    Map inference results → LLMOutput-compatible dict.

    results keys: page_number, pred_label, p_other, p_summons, p_complaint
    """
    # Group by predicted label, skip OTHER unless it's the only group
    groups: dict[str, list[dict]] = {}
    for r in results:
        groups.setdefault(r["pred_label"], []).append(r)

    documents = []
    for label in ("SUMMONS", "COMPLAINT"):
        pages = groups.get(label, [])
        if not pages:
            continue
        documents.append({
            "document_type": _LABEL_TO_DOC_TYPE[label],
            "page_numbers":  sorted(r["page_number"] for r in pages),
            "reasoning": [
                {
                    "page": r["page_number"],
                    "matched_patterns": [
                        f"pred={label}",
                        f"confidence={r[f'p_{label.lower()}']:.4f}",
                    ],
                }
                for r in sorted(pages, key=lambda x: x["page_number"])
            ],
        })

    # Fallback: all pages classified as OTHER
    if not documents:
        other = groups.get("OTHER", results)
        documents = [{
            "document_type": "Other",
            "page_numbers":  sorted(r["page_number"] for r in other),
            "reasoning": [
                {
                    "page": r["page_number"],
                    "matched_patterns": ["pred=OTHER", f"confidence={r['p_other']:.4f}"],
                }
                for r in sorted(other, key=lambda x: x["page_number"])
            ],
        }]

    top10_summons = sorted(
        r["page_number"]
        for r in sorted(results, key=lambda x: x["p_summons"], reverse=True)[:TOP_K]
    )
    top10_complaint = sorted(
        r["page_number"]
        for r in sorted(results, key=lambda x: x["p_complaint"], reverse=True)[:TOP_K]
    )

    return {
        "status":    DEFAULT_STATUS,
        "cost":      DEFAULT_COST,
        "reason":    DEFAULT_REASON,
        "documents": documents,
        "metadata":  {"file_id": str(file_id), "pdf_name": pdf_name, "time_taken_to_process": round(time_taken, 4)},
        "optional_data": {
            "top10_summons_pages":   [str(p) for p in top10_summons],
            "top10_complaint_pages": [str(p) for p in top10_complaint],
        },
    }


def build_response(
    file_id: int,
    pdf_name: str,
    total_pages: int,
    results: list[dict],
) -> dict:
    """
    Parameters
    ----------
    results : list of dicts from run_inference()
        keys: page_number, pred_label, p_other, p_summons, p_complaint
    """
    pred_summons  = sorted(r["page_number"] for r in results if r["pred_label"] == "SUMMONS")
    pred_complaint = sorted(r["page_number"] for r in results if r["pred_label"] == "COMPLAINT")

    top10_summons = sorted(
        r["page_number"]
        for r in sorted(results, key=lambda x: x["p_summons"], reverse=True)[:TOP_K]
    )
    top10_complaint = sorted(
        r["page_number"]
        for r in sorted(results, key=lambda x: x["p_complaint"], reverse=True)[:TOP_K]
    )

    return {
        "file_id":               file_id,
        "pdf_name":              pdf_name,
        "total_pages":           total_pages,
        "pred_summons_pages":    pred_summons,
        "pred_complaint_pages":  pred_complaint,
        "pred_summons_count":    len(pred_summons),
        "pred_complaint_count":  len(pred_complaint),
        "top10_summons_pages":   top10_summons,
        "top10_complaint_pages": top10_complaint,
    }
