from typing import Tuple, Optional
from Command import Command
from Board import Board

class Physics:
    def __init__(self, start_cell: Tuple[int, int],
    board: Board, speed_m_s: float = 1.0):
        self.start_cell = start_cell
        self.current_cell = start_cell
        self.board = board
        self.speed_m_s = speed_m_s
        self.target_cell: Optional[Tuple[int, int]] = None
        self.start_time_ms: Optional[int] = None
        self.move_duration_ms: Optional[int] = None


    def reset(self, cmd: Command):
        """לא ממומש – יש לממש במחלקת משנה"""
        raise NotImplementedError()

    def update(self, now_ms: int) -> Optional[Command]:
        """לא ממומש – יש לממש במחלקת משנה"""
        raise NotImplementedError()

    def get_pos(self) -> Tuple[int, int]:
        """מחזיר את מיקום הפיקסלים של התא הנוכחי"""
        return self.board.cell_to_px(self.current_cell)

    def can_capture(self) -> bool:
        """ברירת מחדל: לא תוקף"""
        return False

    def can_be_captured(self) -> bool:
        """ברירת מחדל: ניתן ללכידה"""
        return True
    def get_draw_position(self, now_ms: int) -> Tuple[int, int]:
        """מחזיר את מיקום הפיקסלים שבו הכלי אמור להופיע כעת"""
        return self.board.cell_to_px(self.current_cell)

    def get_cooldown_ratio(self, now_ms: int) -> float:
        """
        מחזיר יחס קירור (cooldown) בין 0 ל־1.
        1 פירושו שהפעולה הסתיימה, 0 פירושו שעדיין לא התחילה.

        בברירת מחדל – אין קירור, תמיד 1.
        """
        return 1.0

    
class IdlePhysics(Physics):
    def reset(self, cmd: Command):
        self.current_cell =cmd.params[0] if cmd.params else self.start_cell
        self.target_cell = None
        self.start_time_ms = None
        self.move_duration_ms = None

    def update(self, now_ms: int) -> Optional[Command]:
        return None  # אין תנועה, אין שינוי
    
class MovePhysics(Physics):
    def reset(self, cmd: Command):
        self.start_cell = cmd.start_cell
        self.target_cell = cmd.target_cell
        self.start_time_ms = cmd.start_time
        self.current_cell = cmd.start_cell
        src_px = self.board.cell_to_px(self.start_cell)
        dst_px = self.board.cell_to_px(self.target_cell)
        dx = dst_px[0] - src_px[0]
        dy = dst_px[1] - src_px[1]
        dist_px = (dx**2 + dy**2) ** 0.5
        meters = dist_px / self.board.pixels_per_meter
        duration_s = meters / self.speed_m_s
        self.move_duration_ms = int(duration_s * 1000)

    def update(self, now_ms: int) -> Optional[Command]:
        if self.start_time_ms is None or self.target_cell is None:
            return None

        dt = now_ms - self.start_time_ms
        if dt >= self.move_duration_ms:
            self.current_cell = self.target_cell
            return Command(
                name="move_done",
                start_time=now_ms,
                start_cell=self.current_cell,
                target_cell=self.current_cell,
            )
        return None  # עדיין בתנועה
    def get_draw_position(self, now_ms: int) -> Tuple[int, int]:
        if self.start_time_ms is None or self.target_cell is None or self.move_duration_ms is None:
            return self.board.cell_to_px(self.current_cell)

        dt = now_ms - self.start_time_ms
        ratio = min(dt / self.move_duration_ms, 1.0)

        src_px = self.board.cell_to_px(self.start_cell)
        dst_px = self.board.cell_to_px(self.target_cell)

        x = int(src_px[0] + (dst_px[0] - src_px[0]) * ratio)
        y = int(src_px[1] + (dst_px[1] - src_px[1]) * ratio)

        return (x, y)
    def get_cooldown_ratio(self, now_ms: int) -> float:
        if self.start_time_ms is None or self.move_duration_ms is None:
            return 1.0
        elapsed = now_ms - self.start_time_ms
        ratio = elapsed / self.move_duration_ms
        return min(max(ratio, 0.0), 1.0)

    
class JumpPhysics(Physics):
    def reset(self, cmd: Command):
        self.start_cell = cmd.start_cell
        self.target_cell = cmd.target_cell
        self.current_cell = cmd.start_cell
        self.start_time_ms = cmd.start_time

        # תנועה קצרה ומהירה – לדוגמה זמן קפיצה קבוע
        self.move_duration_ms = 200  # קפיצה של 200 מילישניות

    def update(self, now_ms: int) -> Optional[Command]:
        if self.start_time_ms is None or self.target_cell is None:
            return None

        if now_ms - self.start_time_ms >= self.move_duration_ms:
            self.current_cell = self.target_cell
            return Command(
                name="jump_done",
                start_time=now_ms,
                start_cell=self.current_cell,
                target_cell=self.current_cell,
            )
        return None




