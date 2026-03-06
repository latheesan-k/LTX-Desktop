"""Runtime configuration model."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import torch

from runtime_config.model_download_specs import (
    FP8_MODEL_DOWNLOAD_SPECS,
    ModelFileDownloadSpec,
    get_model_download_specs,
)
from state.app_state_types import ModelFileType


@dataclass
class RuntimeConfig:
    device: torch.device
    models_dir: Path
    model_download_specs: Mapping[ModelFileType, ModelFileDownloadSpec]
    required_model_types: frozenset[ModelFileType]
    outputs_dir: Path
    ic_lora_dir: Path
    settings_file: Path
    ltx_api_base_url: str
    force_api_generations: bool
    use_sage_attention: bool
    camera_motion_prompts: dict[str, str]
    default_negative_prompt: str
    fp8_model_download_specs: Mapping[ModelFileType, ModelFileDownloadSpec] = field(
        default_factory=lambda: FP8_MODEL_DOWNLOAD_SPECS,
    )

    def spec_for(self, model_type: ModelFileType) -> ModelFileDownloadSpec:
        return self.model_download_specs[model_type]

    def spec_for_quality(
        self,
        model_type: ModelFileType,
        quality: Literal["full", "quantized"] = "full",
    ) -> ModelFileDownloadSpec:
        """Return the spec for *model_type* respecting the quality preference."""
        specs = get_model_download_specs(quality)
        return specs[model_type]

    def model_path(self, model_type: ModelFileType) -> Path:
        return self.models_dir / self.spec_for(model_type).relative_path

    def model_path_for_quality(
        self,
        model_type: ModelFileType,
        quality: Literal["full", "quantized"] = "full",
    ) -> Path:
        """Return the on-disk path for *model_type* under a given quality."""
        return self.models_dir / self.spec_for_quality(model_type, quality).relative_path

    @property
    def downloading_dir(self) -> Path:
        return self.models_dir / ".downloading"

    def downloading_path(self, model_type: ModelFileType) -> Path:
        """Return the staging path under downloading_dir for a model type."""
        spec = self.spec_for(model_type)
        if spec.is_folder:
            return self.downloading_dir / spec.relative_path
        return self.downloading_dir

    def downloading_path_for_quality(
        self,
        model_type: ModelFileType,
        quality: Literal["full", "quantized"] = "full",
    ) -> Path:
        """Return the staging path under downloading_dir for a quality-specific model."""
        spec = self.spec_for_quality(model_type, quality)
        if spec.is_folder:
            return self.downloading_dir / spec.relative_path
        return self.downloading_dir
