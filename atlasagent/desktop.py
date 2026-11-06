"""Opt-in real desktop adapter. Only run on your own trusted machine.

Requires optional pyautogui dependency. Never expose this adapter via the web API.
"""
from __future__ import annotations
import re

_COORDS = re.compile(r"^([0-9]{1,5}),([0-9]{1,5})$")

class DesktopAdapter:
    def __init__(self):
        try:
            import pyautogui
        except ImportError as exc:
            raise RuntimeError('Install desktop extra: pip install -e ".[desktop]"') from exc
        self.gui = pyautogui
        self.gui.FAILSAFE = True  # Move pointer to top-left corner to abort.
        self.gui.PAUSE = 0.15

    def observe(self) -> str:
        width, height = self.gui.size()
        x, y = self.gui.position()
        return f"Desktop {width}x{height}; pointer at ({x},{y}). Visual understanding not enabled."

    def click(self, target: str) -> str:
        match = _COORDS.fullmatch(target)
        if not match:
            raise ValueError("Target must be x,y coordinates, e.g. 400,300")
        x, y = map(int, match.groups())
        width, height = self.gui.size()
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError("Coordinates outside desktop")
        self.gui.click(x=x, y=y)
        return f"Clicked ({x},{y})"

    def type(self, text: str) -> str:
        if not text or len(text) > 2000:
            raise ValueError("Text must be 1-2000 characters")
        self.gui.write(text, interval=0.015)
        return "Typed text (content excluded from audit)"

    def scroll(self, direction: str) -> str:
        if direction not in ("up", "down"):
            raise ValueError("Scroll must be up or down")
        self.gui.scroll(3 if direction == "up" else -3)
        return "Scrolled " + direction
