import copy
from Command import Command
from Moves import Moves
from Graphics import Graphics
from Physics import Physics
from typing import Dict, Optional


class State:
    def __init__(self, moves: Moves, graphics: Graphics, physics: Physics):
        """Initialize state with moves, graphics, and physics components."""
        self._moves = moves
        self._graphics = graphics
        self._physics = physics
        self.transitions: Dict[str, State] = {}
        self._current_command: Optional[Command] = None
    def clone(self) -> "State":
        """Return a deep copy of the state (excluding transitions)."""
        cloned_state = State(
            moves=copy.deepcopy(self._moves),
            graphics=self._graphics.clone() if hasattr(self._graphics, "clone") else copy.deepcopy(self._graphics),
            physics=self._physics.clone() if hasattr(self._physics, "clone") else copy.deepcopy(self._physics)
        )
        # שיבוץ פקודה אחרונה אם יש
        cloned_state._current_command = copy.deepcopy(self._current_command)
        # העתקת המעברים יכולה להיעשות חיצונית אם רוצים למנוע רקורסיה
        cloned_state.transitions = {}  # ניתן להשלים חיצונית לאחר מכן
        return cloned_state
    def set_transition(self, event: str, target: "State"):
        """Set a transition from this state to another state on an event."""
        self.transitions[event] = target

    def reset(self, cmd: Command):
        """Reset the state with a new command."""
        self._current_command = cmd
        self._graphics.reset(cmd)
        self._physics.reset(cmd)

    def update(self, now_ms: int) -> "State":
        """Update the state based on current time. Return new state if transition is triggered."""
        self._graphics.update(now_ms)
        next_cmd = self._physics.update(now_ms)
        if next_cmd:
            return self.process_command(next_cmd, now_ms)
        return self

    def process_command(self, cmd: Command, now_ms: int) -> "State":
        """Get the next state after processing a command."""
        next_state = self.transitions.get(cmd.type)
        if next_state:
            next_state.reset(cmd)
            return next_state
        return self

    def can_transition(self, event: str) -> bool:
        """Check if a transition for the given event exists."""
        return event in self.transitions

    def get_command(self) -> Optional[Command]:
        """Return the last command that activated this state."""
        return self._current_command

    def get_graphics(self) -> Graphics:
        return self._graphics

    def get_physics(self) -> Physics:
        return self._physics

    def get_moves(self) -> Moves:
        return self._moves
    def set_moves(self,moves):
        """Set the moves for this state."""
        self._moves = moves

    def get_name(self) -> str:
        """Return the name of the state. Override in subclasses if needed."""
        return self.__class__.__name__

    def get_cooldown_ratio(self, now_ms: int) -> float:
        """Return cooldown ratio from 0 to 1 for overlay visualization."""
        return self._physics.get_cooldown_ratio(now_ms)
