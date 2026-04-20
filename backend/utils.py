"""
Shared utility functions.
"""

import json
import re

import numpy as np

_RELEVANT_EXP_RE = re.compile(r"^- ([a-f0-9\-]{36}) \|", re.MULTILINE)


def parse_relevant_uuids(relevant_md: str) -> list[str]:
    """Extract the ordered list of experience UUIDs from a relevant_experience.md file."""
    return _RELEVANT_EXP_RE.findall(relevant_md)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    return float(np.dot(va, vb) / denom) if denom else 0.0


def parse_embedding(json_str: str | None) -> list[float] | None:
    if not json_str:
        return None
    return json.loads(json_str)
