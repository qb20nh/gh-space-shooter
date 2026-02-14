"""Tests for Animator."""

from gh_space_shooter.game import Animator, ColumnStrategy
from gh_space_shooter.game.raster_animation import generate_raster_frames
from gh_space_shooter.github_client import ContributionData


# Sample contribution data for testing
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


def test_generate_frames_returns_iterator():
    """generate_frames should return an iterator of PIL Images."""
    strategy = ColumnStrategy()
    animator = Animator(SAMPLE_DATA, strategy, fps=30)

    frames = list(animator.generate_frames())

    assert len(frames) > 0
    assert all(hasattr(f, "save") for f in frames)  # PIL Images have save method


def test_generate_raster_frames_returns_iterator():
    """Raster adapter should return an iterator of PIL Images."""
    strategy = ColumnStrategy()
    animator = Animator(SAMPLE_DATA, strategy, fps=30)

    frames = list(generate_raster_frames(animator))

    assert len(frames) > 0
    assert all(hasattr(f, "save") for f in frames)


def test_iter_state_timeline_returns_elapsed_time_sequence():
    """iter_state_timeline should emit mutable state snapshots with elapsed ms."""
    strategy = ColumnStrategy()
    animator = Animator(SAMPLE_DATA, strategy, fps=20)

    timeline = list(animator.iter_state_timeline(max_frames=5))

    assert len(timeline) == 5
    elapsed = [item[1] for item in timeline]
    assert elapsed == [0, 50, 100, 150, 200]


def test_iter_state_timeline_respects_max_frames():
    """iter_state_timeline should stop at the requested max frame count."""
    strategy = ColumnStrategy()
    animator = Animator(SAMPLE_DATA, strategy, fps=30)

    timeline = list(animator.iter_state_timeline(max_frames=3))

    assert len(timeline) == 3
