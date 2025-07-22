import pathlib
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import copy
from img import Img
from Command import Command
from Board import Board


class Graphics:
    def __init__(self,
                 sprites_folder: pathlib.Path,
                 board: Board,
                 loop: bool = True,
                 fps: float = 6.0):
        """Initialize graphics with sprites folder, cell size, loop setting, and FPS."""
        self.sprites_folder = sprites_folder
        self.board = board
        self.loop = loop
        self.fps = fps
        self.frame_duration_ms = int(1000 / fps)
        
        # Load all sprite images
        self.sprites = []
        self._load_sprites()
        
        # Animation state
        self.current_frame = 0
        self.last_frame_time = 0
        self.is_playing = False
        self.start_time_ms = None

    def _load_sprites(self):
        """Load all sprite images from the folder."""
        self.sprites = []
        if not self.sprites_folder.exists():
            # Create a default sprite if folder doesn't exist
            default_img = Img()
            # Create a simple colored rectangle as default
            import numpy as np
            default_pixels = np.full(
                (self.board.cell_H_pix, self.board.cell_W_pix, 3), 
                [128, 128, 128], 
                dtype=np.uint8
            )
            default_img.img = default_pixels
            self.sprites.append(default_img)
            return
            
        # Look for common image extensions
        extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
        sprite_files = []
        
        for ext in extensions:
            sprite_files.extend(sorted(self.sprites_folder.glob(ext)))
        
        if not sprite_files:
            # No sprites found, create default
            self._create_default_sprite()
            return
            
        # Load each sprite file
        cell_size = (self.board.cell_W_pix, self.board.cell_H_pix)
        for sprite_file in sprite_files:
            try:
                sprite = Img().read(sprite_file, size=cell_size, keep_aspect=False)
                self.sprites.append(sprite)
            except Exception as e:
                print(f"Warning: Could not load sprite {sprite_file}: {e}")
                
        # If no sprites loaded successfully, create default
        if not self.sprites:
            self._create_default_sprite()

    def _create_default_sprite(self):
        """Create a default sprite when no images are found."""
        import numpy as np
        default_img = Img()
        default_pixels = np.full(
            (self.board.cell_H_pix, self.board.cell_W_pix, 3), 
            [100, 150, 200], 
            dtype=np.uint8
        )
        default_img.img = default_pixels
        self.sprites.append(default_img)

    def copy(self):
        """Create a shallow copy of the graphics object."""
        new_graphics = Graphics(
            self.sprites_folder,
            self.board,
            self.loop,
            self.fps
        )
        new_graphics.sprites = [sprite.copy() for sprite in self.sprites]
        new_graphics.current_frame = self.current_frame
        new_graphics.last_frame_time = self.last_frame_time
        new_graphics.is_playing = self.is_playing
        new_graphics.start_time_ms = self.start_time_ms
        return new_graphics

    def reset(self, cmd: Command):
        """Reset the animation with a new command."""
        self.current_frame = 0
        self.start_time_ms = cmd.timestamp
        self.last_frame_time = cmd.timestamp
        self.is_playing = True

    def update(self, now_ms: int):
        """Advance animation frame based on game-loop time, not wall time."""
        if not self.is_playing or self.start_time_ms is None:
            return
            
        # Calculate which frame we should be on based on elapsed time
        elapsed_ms = now_ms - self.start_time_ms
        target_frame = int(elapsed_ms // self.frame_duration_ms)
        
        if len(self.sprites) <= 1:
            # Single frame or no sprites
            self.current_frame = 0
            return
            
        if self.loop:
            # Loop through frames
            self.current_frame = target_frame % len(self.sprites)
        else:
            # Play once and stop at last frame
            if target_frame >= len(self.sprites):
                self.current_frame = len(self.sprites) - 1
                self.is_playing = False
            else:
                self.current_frame = target_frame

    def get_img(self) -> Img:
        """Get the current frame image."""
        if not self.sprites:
            self._create_default_sprite()
            
        if self.current_frame >= len(self.sprites):
            self.current_frame = len(self.sprites) - 1
            
        return self.sprites[self.current_frame].copy()

    def is_animation_complete(self) -> bool:
        """Check if the animation has completed (for non-looping animations)."""
        if self.loop:
            return False
        return not self.is_playing and self.current_frame == len(self.sprites) - 1