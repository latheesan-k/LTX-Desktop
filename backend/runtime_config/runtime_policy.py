"""Runtime policy decisions for forced API mode."""

from __future__ import annotations

# Full-precision (bfloat16) models need ~31 GB VRAM.
# FP8 quantized models need roughly half: ~12 GB.
_VRAM_THRESHOLD_FULL = 31
_VRAM_THRESHOLD_QUANTIZED = 12


def decide_force_api_generations(
    system: str,
    cuda_available: bool,
    vram_gb: int | None,
    model_quality: str = "full",
) -> bool:
    """Return whether API-only generation must be forced for this runtime."""
    if system == "Darwin":
        return True

    if system in ("Windows", "Linux"):
        if not cuda_available:
            return True
        if vram_gb is None:
            return True
        threshold = _VRAM_THRESHOLD_QUANTIZED if model_quality == "quantized" else _VRAM_THRESHOLD_FULL
        return vram_gb < threshold

    return True
