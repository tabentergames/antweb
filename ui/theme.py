"""F2 theme tokens and mode switching for TabX."""


class Theme:
    """Centralized visual tokens used by the PyQt6 shell."""

    _mode = "light"

    _palettes = {
        "light": {
            "bg": "#f6f7fb",
            "panel": "#fbfbfe",
            "panel_alt": "#f1f3f8",
            "card": "#ffffff",
            "border": "#e2e6ef",
            "border_soft": "#edf0f6",
            "text": "#172033",
            "muted": "#6b7280",
            "subtle": "#9aa4b2",
            "purple": "#7c5cff",
            "blue": "#2f80ed",
            "purple_soft": "#f0edff",
            "blue_soft": "#eaf3ff",
            "button": "#ffffff",
            "button_hover": "#f1f3f8",
            "tab_inactive": "#eef1f7",
            "tab_hover": "#ffffff",
            "input": "#ffffff",
            "toolbar": "rgba(251, 251, 254, 0.96)",
            "shadow": "rgba(31, 41, 55, 0.08)",
        },
        "dark": {
            "bg": "#10131a",
            "panel": "#171b24",
            "panel_alt": "#202634",
            "card": "#1d2330",
            "border": "#303746",
            "border_soft": "#252b38",
            "text": "#eef2f8",
            "muted": "#a6afbd",
            "subtle": "#737f91",
            "purple": "#9b87ff",
            "blue": "#6bb6ff",
            "purple_soft": "#2a2547",
            "blue_soft": "#1b314b",
            "button": "#202634",
            "button_hover": "#293143",
            "tab_inactive": "#202634",
            "tab_hover": "#252d3d",
            "input": "#111722",
            "toolbar": "rgba(23, 27, 36, 0.96)",
            "shadow": "rgba(0, 0, 0, 0.24)",
        },
    }

    @classmethod
    def configure(cls, mode):
        cls._mode = "dark" if mode == "dark" else "light"
        for key, value in cls._palettes[cls._mode].items():
            setattr(cls, key, value)
        cls.qss = cls._build_qss()

    @classmethod
    def mode(cls):
        return cls._mode

    @classmethod
    def opposite_mode(cls):
        return "dark" if cls._mode == "light" else "light"

    @classmethod
    def _build_qss(cls):
        return f"""
            QWidget {{
                font-family: Arial;
                color: {cls.text};
            }}
            QPushButton {{
                font-weight: 600;
            }}
            QToolTip {{
                background-color: #111827;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 8px;
            }}
        """


Theme.configure("light")

