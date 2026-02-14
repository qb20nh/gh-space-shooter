"""Tests for shared animation encoding pipeline."""

from collections.abc import Iterator

from PIL import Image

from gh_space_shooter.animation_pipeline import encode_animation
from gh_space_shooter.game.animator import Animator
from gh_space_shooter.game.strategies.base_strategy import BaseStrategy
from gh_space_shooter.game.strategies.column_strategy import ColumnStrategy
from gh_space_shooter.github_client import ContributionData
from gh_space_shooter.output.base import OutputProvider


SAMPLE_DATA: ContributionData = {
    "username": "testuser",
    "total_contributions": 9,
    "weeks": [
        {
            "days": [
                {"level": 1, "date": "2024-01-01", "count": 1},
                {"level": 0, "date": "2024-01-02", "count": 0},
                {"level": 2, "date": "2024-01-03", "count": 3},
                {"level": 0, "date": "2024-01-04", "count": 0},
                {"level": 0, "date": "2024-01-05", "count": 0},
                {"level": 3, "date": "2024-01-06", "count": 5},
                {"level": 0, "date": "2024-01-07", "count": 0},
            ]
        }
    ],
}


class _RasterSpyProvider(OutputProvider[Image.Image]):
    def __init__(self) -> None:
        super().__init__("dummy.bin")
        self.seen_frame_count = 0

    def encode(self, frames: Iterator[Image.Image], frame_duration: int) -> bytes:
        del frame_duration
        frame_list = list(frames)
        self.seen_frame_count = len(frame_list)
        assert all(hasattr(frame, "save") for frame in frame_list)
        return b"raster-ok"


class _CustomFrameProvider(OutputProvider[int]):
    def __init__(self) -> None:
        super().__init__("custom.bin")

    def frame_stream(
        self, animator: Animator, max_frames: int | None
    ) -> Iterator[int] | None:
        del animator
        del max_frames
        return iter([1, 2, 3])

    def encode(self, frames: Iterator[int], frame_duration: int) -> bytes:
        del frame_duration
        return str(sum(frames)).encode("ascii")


class _NoopStrategy(BaseStrategy):
    def generate_actions(self, game_state):
        del game_state
        return iter(())


def test_encode_animation_uses_default_raster_stream_when_provider_has_no_override() -> None:
    provider = _RasterSpyProvider()

    encoded = encode_animation(
        data=SAMPLE_DATA,
        strategy=ColumnStrategy(),
        output_path="output.gif",
        fps=30,
        watermark=False,
        max_frames=5,
        provider=provider,
    )

    assert encoded == b"raster-ok"
    assert provider.seen_frame_count == 5


def test_encode_animation_uses_provider_custom_frame_stream() -> None:
    provider = _CustomFrameProvider()

    encoded = encode_animation(
        data=SAMPLE_DATA,
        strategy=_NoopStrategy(),
        output_path="custom.any",
        fps=30,
        watermark=False,
        max_frames=20,
        provider=provider,
    )

    assert encoded == b"6"
