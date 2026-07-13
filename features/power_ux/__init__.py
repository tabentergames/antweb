"""F7 Power UX modules."""

from .command_palette import CommandPalette, PaletteCommand
from .split_view import SplitViewController
from .sidebar_panels import SidebarWebPanel
from .mouse_gestures import MouseGestureController
from .screenshot import ScreenshotController

__all__ = ["CommandPalette", "MouseGestureController", "PaletteCommand", "ScreenshotController", "SidebarWebPanel", "SplitViewController"]
