"""Animator for generating animations from game strategies."""

from typing import Iterator

from PIL import Image

from ..github_client import ContributionData
from .game_state import GameState
from .render_context import RenderContext
from .renderer import Renderer
from .strategies.base_strategy import BaseStrategy


class Animator:
    """Generates animations from game strategies."""

    def __init__(
        self,
        contribution_data: ContributionData,
        strategy: BaseStrategy,
        fps: int,
        watermark: bool = False,
    ):
        """
        Initialize animator.

        Args:
            contribution_data: The GitHub contribution data
            strategy: The strategy to use for clearing enemies
            fps: Frames per second for the animation
            watermark: Whether to add watermark to output frames
        """
        self.contribution_data = contribution_data
        self.strategy = strategy
        self.fps = fps
        self.watermark = watermark
        self.frame_duration = 1000 // fps
        # Delta time in seconds per frame
        # Used to scale all speeds (cells/second) to per-frame movement
        self.delta_time = 1.0 / fps

    def generate_frames(self, max_frames: int | None = None) -> Iterator[Image.Image]:
        """Generate raster animation frames."""
        renderer: Renderer | None = None
        for game_state, _elapsed_ms in self.iter_state_timeline(max_frames=max_frames):
            if renderer is None:
                renderer = Renderer(
                    game_state,
                    RenderContext.darkmode(),
                    watermark=self.watermark,
                )
            yield renderer.render_frame()

    def iter_state_timeline(
        self, max_frames: int | None = None
    ) -> Iterator[tuple[GameState, int]]:
        """Yield mutable game-state frames with elapsed time in milliseconds."""
        game_state = GameState(self.contribution_data)
        yield from self._iter_state_timeline(game_state, max_frames=max_frames)

    def _iter_state_timeline(
        self, game_state: GameState, max_frames: int | None = None
    ) -> Iterator[tuple[GameState, int]]:
        """Yield mutable game-state frames with elapsed time in milliseconds."""
        rendered = 0
        elapsed_ms = 0
        for _ in self._frame_steps(game_state):
            if max_frames is not None and rendered >= max_frames:
                break
            yield game_state, elapsed_ms
            rendered += 1
            elapsed_ms += self.frame_duration

    def _frame_steps(self, game_state: GameState) -> Iterator[None]:
        """
        Generate frame ticks by mutating game state over time.

        Args:
            game_state: The game state
        """
        # Initial frame showing starting state
        yield None

        # Process each action from the strategy
        for action in self.strategy.generate_actions(game_state):
            game_state.ship.move_to(action.x)
            while game_state.can_take_action() is False:
                game_state.animate(self.delta_time)
                yield None

            if action.shoot:
                game_state.shoot()
                game_state.animate(self.delta_time)
                yield None

        force_kill_countdown = 100
        # Final frames showing completion
        while not game_state.is_complete():
            game_state.animate(self.delta_time)
            yield None

            force_kill_countdown -= 1
            if force_kill_countdown <= 0:
                break

        for _ in range(5):
            yield None
