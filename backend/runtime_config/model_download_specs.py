"""Canonical model download specs and required-model policy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from state.app_state_types import ModelFileType

ModelQualityType = Literal["full", "quantized"]


@dataclass(frozen=True, slots=True)
class ModelFileDownloadSpec:
    relative_path: Path
    expected_size_bytes: int
    is_folder: bool
    repo_id: str
    description: str

    @property
    def name(self) -> str:
        return self.relative_path.name


MODEL_FILE_ORDER: tuple[ModelFileType, ...] = (
    "checkpoint",
    "upsampler",
    "text_encoder",
    "zit",
)


DEFAULT_MODEL_DOWNLOAD_SPECS: dict[ModelFileType, ModelFileDownloadSpec] = {
    "checkpoint": ModelFileDownloadSpec(
        relative_path=Path("ltx-2.3-22b-distilled.safetensors"),
        expected_size_bytes=43_000_000_000,
        is_folder=False,
        repo_id="Lightricks/LTX-2.3",
        description="Main transformer model",
    ),
    "upsampler": ModelFileDownloadSpec(
        relative_path=Path("ltx-2.3-spatial-upscaler-x2-1.0.safetensors"),
        expected_size_bytes=1_900_000_000,
        is_folder=False,
        repo_id="Lightricks/LTX-2.3",
        description="2x Upscaler",
    ),
    "text_encoder": ModelFileDownloadSpec(
        relative_path=Path("gemma-3-12b-it-qat-q4_0-unquantized"),
        expected_size_bytes=25_000_000_000,
        is_folder=True,
        repo_id="Lightricks/gemma-3-12b-it-qat-q4_0-unquantized",
        description="Gemma text encoder (bfloat16)",
    ),
    "zit": ModelFileDownloadSpec(
        relative_path=Path("Z-Image-Turbo"),
        expected_size_bytes=31_000_000_000,
        is_folder=True,
        repo_id="Tongyi-MAI/Z-Image-Turbo",
        description="Z-Image-Turbo model for text-to-image generation",
    ),
}

FP8_MODEL_DOWNLOAD_SPECS: dict[ModelFileType, ModelFileDownloadSpec] = {
    "checkpoint": ModelFileDownloadSpec(
        relative_path=Path("ltx-2.3-22b-dev-fp8.safetensors"),
        expected_size_bytes=27_100_000_000,
        is_folder=False,
        repo_id="Lightricks/LTX-2.3-fp8",
        description="Main transformer model (FP8 quantized)",
    ),
}


def get_model_download_specs(
    quality: ModelQualityType = "full",
) -> dict[ModelFileType, ModelFileDownloadSpec]:
    """Return the full spec dict for a given quality level.

    For 'quantized', the checkpoint entry is replaced with the FP8 variant.
    All other model types (upsampler, text_encoder, zit) remain unchanged.
    """
    if quality == "quantized":
        merged = dict(DEFAULT_MODEL_DOWNLOAD_SPECS)
        merged.update(FP8_MODEL_DOWNLOAD_SPECS)
        return merged
    return dict(DEFAULT_MODEL_DOWNLOAD_SPECS)


DEFAULT_REQUIRED_MODEL_TYPES: frozenset[ModelFileType] = frozenset(
    {"checkpoint", "upsampler", "zit"}
)


def resolve_required_model_types(
    base_required: frozenset[ModelFileType],
    has_api_key: bool,
    use_local_text_encoder: bool = False,
) -> frozenset[ModelFileType]:
    if not base_required:
        return base_required
    if has_api_key and not use_local_text_encoder:
        return base_required
    return cast(frozenset[ModelFileType], base_required | {"text_encoder"})
