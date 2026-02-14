"""Shared animation orchestration used by CLI and web app entry points."""

from typing import Any, Iterator

from .game.animator import Animator
from .game.raster_animation import generate_raster_frames
from .game.strategies.base_strategy import BaseStrategy
from .github_client import ContributionData
from .output import resolve_output_provider
from .output.base import OutputProvider


def build_frame_stream(
    animator: Animator,
    provider: OutputProvider[Any],
    max_frames: int | None,
) -> Iterator[Any]:
    """Build the frame stream for the target output provider."""
    custom_stream = provider.frame_stream(animator, max_frames)
    if custom_stream is not None:
        return custom_stream
    return generate_raster_frames(animator, max_frames)


def encode_animation(
    data: ContributionData,
    strategy: BaseStrategy,
    output_path: str,
    *,
    fps: int,
    watermark: bool,
    max_frames: int | None,
    provider: OutputProvider[Any] | None = None,
) -> bytes:
    """Encode animation bytes for the given strategy and output path."""
    target_provider = provider or resolve_output_provider(output_path)
    animator = Animator(data, strategy, fps=fps, watermark=watermark)
    frame_stream = build_frame_stream(
        animator,
        provider=target_provider,
        max_frames=max_frames,
    )
    return target_provider.encode(frame_stream, frame_duration=1000 // fps)
