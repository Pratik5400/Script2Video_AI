"""
P36 - Script2Video AI
U3: BLIP Verification & Semantic Cosine Similarity Service

This service handles:
1. Ingestion and parsing of BLIP captions and verification results from Colab.
2. Raw cosine similarity evaluation with a clearly labeled heuristic threshold.
3. Manual review overrides (Approved / Needs Review / Rejected + Notes).
4. Exporting structured JSON and Markdown verification reports.
"""

import json
import math
import re
from pathlib import Path
from typing import Union, Dict, Any, List, Optional

DEFAULT_HEURISTIC_THRESHOLD = 0.40


def load_verification_results(source_dir_or_file: Union[str, Path] = "generated") -> List[Dict[str, Any]]:
    """
    Load verification_results.json from a directory or specific file path.
    """
    path = Path(source_dir_or_file)
    if path.is_dir():
        target = path / "verification_results.json"
    else:
        target = path

    if not target.exists():
        return []

    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def load_caption_results(source_dir_or_file: Union[str, Path] = "generated") -> List[Dict[str, Any]]:
    """
    Load caption_results.json from a directory or specific file path.
    """
    path = Path(source_dir_or_file)
    if path.is_dir():
        target = path / "caption_results.json"
    else:
        target = path

    if not target.exists():
        return []

    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def calculate_cosine_similarity_tokens(text1: str, text2: str) -> float:
    """
    Calculate raw cosine similarity between two texts using term-frequency vectors.
    Acts as a pure-Python fallback for local testing without requiring heavy ML libraries.

    Note:
        Returns raw cosine similarity in [-1.0, 1.0].
        This is a geometric similarity metric, NOT classification accuracy.
    """
    def tokenize(s: str) -> List[str]:
        return re.findall(r"\b[a-zA-Z0-9_]+\b", s.lower())

    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)

    if not tokens1 or not tokens2:
        return 0.0

    tf1: Dict[str, float] = {}
    tf2: Dict[str, float] = {}

    for t in tokens1:
        tf1[t] = tf1.get(t, 0.0) + 1.0
    for t in tokens2:
        tf2[t] = tf2.get(t, 0.0) + 1.0

    all_terms = set(tf1.keys()).union(set(tf2.keys()))

    dot_product = sum(tf1.get(term, 0.0) * tf2.get(term, 0.0) for term in all_terms)
    norm1 = math.sqrt(sum(val ** 2 for val in tf1.values()))
    norm2 = math.sqrt(sum(val ** 2 for val in tf2.values()))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0

    cosine_sim = dot_product / (norm1 * norm2)
    # Ensure float precision bounds
    return max(-1.0, min(1.0, cosine_sim))


def evaluate_heuristic_status(
    cosine_sim: Optional[float],
    threshold: float = DEFAULT_HEURISTIC_THRESHOLD,
    error: Optional[str] = None
) -> str:
    """
    Evaluate verification status based on a configurable heuristic threshold.

    IMPORTANT:
        The threshold is an exploratory heuristic indicator for guiding human review,
        NOT a scientifically validated threshold or classification accuracy metric.
    """
    if error or cosine_sim is None:
        return "Needs Review (Missing/Error)"

    if cosine_sim >= threshold:
        return "Relevant"
    else:
        return "Needs Review (Heuristic)"


def apply_heuristic_threshold(
    records: List[Dict[str, Any]],
    threshold: float
) -> List[Dict[str, Any]]:
    """
    Re-evaluate verification_status across records given a new heuristic threshold.
    Preserves manual review overrides and raw cosine similarity values.
    """
    updated = []
    for record in records:
        rec = dict(record)
        rec["heuristic_threshold"] = round(threshold, 2)
        cos_sim = rec.get("cosine_similarity")
        err = rec.get("error")
        rec["verification_status"] = evaluate_heuristic_status(cos_sim, threshold, err)
        updated.append(rec)
    return updated


def update_manual_review(
    records: List[Dict[str, Any]],
    scene_number: int,
    manual_status: str,
    notes: str = ""
) -> List[Dict[str, Any]]:
    """
    Update manual review status and notes for a specific scene.
    Allowed manual statuses: "Pending", "Approved (Manual)", "Flagged for Revision", "Rejected".
    """
    updated = []
    for record in records:
        rec = dict(record)
        if rec.get("scene_number") == scene_number:
            rec["manual_review_status"] = manual_status
            rec["manual_notes"] = notes.strip()
        updated.append(rec)
    return updated


def generate_verification_summary(
    records: List[Dict[str, Any]],
    threshold: float = DEFAULT_HEURISTIC_THRESHOLD
) -> Dict[str, Any]:
    """
    Compute summary statistics across verification records.
    """
    total = len(records)
    valid_scores = [
        r["cosine_similarity"] for r in records
        if r.get("cosine_similarity") is not None
    ]

    relevant_count = sum(
        1 for r in records
        if r.get("verification_status") == "Relevant"
    )
    needs_review_count = total - relevant_count

    manual_approved = sum(
        1 for r in records
        if "Approved" in str(r.get("manual_review_status", ""))
    )
    manual_flagged = sum(
        1 for r in records
        if "Flagged" in str(r.get("manual_review_status", "")) or "Rejected" in str(r.get("manual_review_status", ""))
    )
    manual_pending = total - manual_approved - manual_flagged

    avg_score = (sum(valid_scores) / len(valid_scores)) if valid_scores else None
    min_score = min(valid_scores) if valid_scores else None
    max_score = max(valid_scores) if valid_scores else None

    return {
        "total_scenes": total,
        "scored_scenes": len(valid_scores),
        "relevant_scenes": relevant_count,
        "needs_review_scenes": needs_review_count,
        "heuristic_threshold": threshold,
        "average_cosine_similarity": round(avg_score, 4) if avg_score is not None else None,
        "min_cosine_similarity": round(min_score, 4) if min_score is not None else None,
        "max_cosine_similarity": round(max_score, 4) if max_score is not None else None,
        "manual_approved": manual_approved,
        "manual_flagged": manual_flagged,
        "manual_pending": manual_pending
    }


def export_verification_report_markdown(
    records: List[Dict[str, Any]],
    summary: Optional[Dict[str, Any]] = None,
    project_title: str = "Script2Video AI - Unit 3 Verification Report"
) -> str:
    """
    Generate a comprehensive Markdown verification report.
    Explicitly states that cosine similarity is a vector metric and threshold is heuristic.
    """
    if summary is None:
        summary = generate_verification_summary(records)

    avg_sim = summary.get("average_cosine_similarity")
    min_sim = summary.get("min_cosine_similarity")
    max_sim = summary.get("max_cosine_similarity")

    avg_sim_str = f"{avg_sim:+.4f}" if avg_sim is not None else "N/A"
    min_sim_str = f"{min_sim:+.4f}" if min_sim is not None else "N/A"
    max_sim_str = f"{max_sim:+.4f}" if max_sim is not None else "N/A"

    md = [
        f"# {project_title}\n",
        "## Generative AI Verification Report (BLIP + Sentence Transformers)\n",
        "> **Important Methodology Note:**\n",
        "> Similarity scores report raw **Cosine Similarity** between sentence embeddings "
        "(`sentence-transformers/all-MiniLM-L6-v2`) of the intended visual description and the BLIP-generated caption. "
        "Cosine similarity measures angle in vector space (range: -1.0 to +1.0) and is **not** classification accuracy. "
        f"The review threshold ({summary['heuristic_threshold']:.2f}) is an exploratory **heuristic** indicator to assist "
        "human curation, not an absolute automated guarantee.\n",
        "### 1. Executive Summary\n",
        f"- **Total Scenes Evaluated:** {summary['total_scenes']}",
        f"- **Relevant (Heuristic):** {summary['relevant_scenes']}",
        f"- **Needs Review (Heuristic):** {summary['needs_review_scenes']}",
        f"- **Configurable Heuristic Threshold:** {summary['heuristic_threshold']:.2f}",
        f"- **Average Cosine Similarity:** {avg_sim_str}",
        f"- **Min / Max Similarity:** {min_sim_str} / {max_sim_str}",
        f"- **Manual Review Status:** {summary['manual_approved']} Approved, {summary['manual_flagged']} Flagged, {summary['manual_pending']} Pending\n",
        "### 2. Scene-by-Scene Verification Table\n",
        "| Scene | Title | Image File | BLIP Caption | Cosine Sim | Heuristic Status | Manual Review |",
        "| :---: | :--- | :--- | :--- | :---: | :---: | :---: |"
    ]

    for r in records:
        s_num = r.get("scene_number", "-")
        title = r.get("scene_title", "-")
        img_fn = r.get("image_filename", "-")
        caption = r.get("blip_caption", r.get("error", "N/A"))
        if caption and len(caption) > 40:
            caption_short = caption[:37] + "..."
        else:
            caption_short = caption or "N/A"

        sim = r.get("cosine_similarity")
        sim_str = f"{sim:+.4f}" if sim is not None else "N/A"
        h_status = r.get("verification_status", "N/A")
        m_status = r.get("manual_review_status", "Pending")

        md.append(f"| {s_num} | {title} | `{img_fn}` | {caption_short} | `{sim_str}` | {h_status} | {m_status} |")

    md.append("\n### 3. Detailed Scene Findings\n")
    for r in records:
        s_num = r.get("scene_number", "-")
        title = r.get("scene_title", "-")
        expected = r.get("original_visual_description", "N/A")
        caption = r.get("blip_caption", "N/A")
        sim = r.get("cosine_similarity")
        sim_str = f"{sim:+.4f}" if sim is not None else "N/A"
        h_status = r.get("verification_status", "N/A")
        m_status = r.get("manual_review_status", "Pending")
        notes = r.get("manual_notes", "")
        error = r.get("error")

        md.append(f"#### Scene {s_num}: {title}")
        md.append(f"- **Original Visual Description:** {expected}")
        md.append(f"- **BLIP Caption:** {caption}")
        md.append(f"- **Raw Cosine Similarity:** `{sim_str}`")
        md.append(f"- **Heuristic Evaluation:** `{h_status}`")
        md.append(f"- **Manual Review:** `{m_status}`" + (f" ({notes})" if notes else ""))
        if error:
            md.append(f"- **Recorded Error:** `{error}`")
        md.append("")

    return "\n".join(md)


def export_verification_report_json(
    records: List[Dict[str, Any]],
    output_path: Union[str, Path] = "generated/verification_results.json"
) -> Path:
    """
    Save the verification records into a JSON file.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)
    return out
