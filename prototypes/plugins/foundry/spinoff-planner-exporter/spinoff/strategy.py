"""Map lifecycle classifications to spin-off export strategies."""

from __future__ import annotations

CLASSIFICATION_TO_STRATEGY = {
    "REUSE": "REUSE_SHARED",
    "EXPORT": "EXPORT_COPY",
    "REMOTE": "REMOTE",
    "PROMOTE_SHARED": "PROMOTE_SHARED",
    "DROP": "DROP",
}

BLOCKING_CLASSIFICATIONS = frozenset({"PROMOTE", "UNKNOWN"})
VALID_STRATEGIES = frozenset(CLASSIFICATION_TO_STRATEGY.values())


def map_classification(classification: str) -> str:
    if classification in BLOCKING_CLASSIFICATIONS:
        raise ValueError(f"{classification} classification blocks export")
    try:
        return CLASSIFICATION_TO_STRATEGY[classification]
    except KeyError as exc:
        raise ValueError(f"unsupported classification: {classification}") from exc
