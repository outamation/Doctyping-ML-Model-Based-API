"""
Build a ClassifyResponse from raw per-page inference results.
"""
from __future__ import annotations

TOP_K = 10


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
