"""Tests for runtime policy decision helper."""

from __future__ import annotations

from runtime_config.runtime_policy import decide_force_api_generations


def test_darwin_always_forces_api() -> None:
    assert decide_force_api_generations(system="Darwin", cuda_available=True, vram_gb=24) is True
    assert decide_force_api_generations(system="Darwin", cuda_available=False, vram_gb=None) is True


def test_windows_without_cuda_forces_api() -> None:
    assert decide_force_api_generations(system="Windows", cuda_available=False, vram_gb=24) is True


def test_windows_with_low_vram_forces_api() -> None:
    assert decide_force_api_generations(system="Windows", cuda_available=True, vram_gb=30) is True


def test_windows_with_unknown_vram_forces_api() -> None:
    assert decide_force_api_generations(system="Windows", cuda_available=True, vram_gb=None) is True


def test_windows_with_required_vram_allows_local_mode() -> None:
    assert decide_force_api_generations(system="Windows", cuda_available=True, vram_gb=31) is False


def test_linux_without_cuda_forces_api() -> None:
    assert decide_force_api_generations(system="Linux", cuda_available=False, vram_gb=24) is True


def test_linux_with_low_vram_forces_api() -> None:
    assert decide_force_api_generations(system="Linux", cuda_available=True, vram_gb=30) is True


def test_linux_with_unknown_vram_forces_api() -> None:
    assert decide_force_api_generations(system="Linux", cuda_available=True, vram_gb=None) is True


def test_linux_with_required_vram_allows_local_mode() -> None:
    assert decide_force_api_generations(system="Linux", cuda_available=True, vram_gb=31) is False


def test_quantized_lowers_vram_threshold() -> None:
    # 16 GB is below full threshold (31) but above quantized threshold (12)
    assert decide_force_api_generations(system="Linux", cuda_available=True, vram_gb=16, model_quality="full") is True
    assert decide_force_api_generations(system="Linux", cuda_available=True, vram_gb=16, model_quality="quantized") is False
    assert decide_force_api_generations(system="Windows", cuda_available=True, vram_gb=16, model_quality="full") is True
    assert decide_force_api_generations(system="Windows", cuda_available=True, vram_gb=16, model_quality="quantized") is False


def test_auto_uses_lowest_threshold() -> None:
    # "auto" (first run, no settings yet) uses quantized threshold so the
    # user can reach the setup flow and pick quality.
    assert decide_force_api_generations(system="Linux", cuda_available=True, vram_gb=16, model_quality="auto") is False
    assert decide_force_api_generations(system="Windows", cuda_available=True, vram_gb=24, model_quality="auto") is False
    # Still forces API when below even the quantized threshold
    assert decide_force_api_generations(system="Linux", cuda_available=True, vram_gb=8, model_quality="auto") is True


def test_quantized_still_requires_cuda() -> None:
    assert decide_force_api_generations(system="Linux", cuda_available=False, vram_gb=16, model_quality="quantized") is True


def test_quantized_with_very_low_vram_forces_api() -> None:
    assert decide_force_api_generations(system="Linux", cuda_available=True, vram_gb=8, model_quality="quantized") is True


def test_quantized_darwin_still_forces_api() -> None:
    assert decide_force_api_generations(system="Darwin", cuda_available=True, vram_gb=48, model_quality="quantized") is True


def test_other_systems_fail_closed() -> None:
    assert decide_force_api_generations(system="FreeBSD", cuda_available=True, vram_gb=48) is True
