"""F2 theme tokens and mode switching for TabX."""


class Theme:
    """Centralized visual tokens used by the PyQt6 shell."""

    _mode = "light"

    # Bosluk skalasi (px) — layout margin/spacing degerleri buradan secilir.
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 12
    SPACE_LG = 16
    SPACE_XL = 24

    # Kose yaricapi skalasi (px).
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 18
    RADIUS_PILL = 999

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
            "subtle": "#64708a",
            "purple": "#7c5cff",
            "blue": "#2f80ed",
            # Durum/sinyal renkleri — risk ve basari mesajlari yalnizca
            # bu tokenlardan gelir, sayfa iclerinde sabit hex yazilmaz.
            "danger": "#c0392b",
            "success": "#117a43",
            # Klavye odagi/focus halkasi — purple ailesinden turetilmis.
            "focus_ring": "#b7a7ff",
            "purple_soft": "#f0edff",
            "blue_soft": "#eaf3ff",
            "button": "#ffffff",
            "button_hover": "#f1f3f8",
            "tab_inactive": "#eef1f7",
            "tab_hover": "#ffffff",
            "input": "#ffffff",
            "toolbar": "rgba(251, 251, 254, 0.96)",
            "shadow": "rgba(31, 41, 55, 0.08)",
            # Seffaf (glass) yuzeyler — panel/overlay'lerde duz panel rengi
            # yerine bunlar kullanilirsa altta kalan icerik hissedilir.
            "glass": "rgba(251, 251, 254, 0.78)",
            "glass_strong": "rgba(251, 251, 254, 0.92)",
            "glass_border": "rgba(23, 32, 51, 0.10)",
            "scrim": "rgba(23, 32, 51, 0.32)",
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
            "subtle": "#8a96a8",
            "purple": "#9b87ff",
            "blue": "#6bb6ff",
            "danger": "#ef6e61",
            "success": "#3ecf8e",
            "focus_ring": "#8f7bff",
            "purple_soft": "#2a2547",
            "blue_soft": "#1b314b",
            "button": "#202634",
            "button_hover": "#293143",
            "tab_inactive": "#202634",
            "tab_hover": "#252d3d",
            "input": "#111722",
            "toolbar": "rgba(23, 27, 36, 0.96)",
            "shadow": "rgba(0, 0, 0, 0.24)",
            "glass": "rgba(23, 27, 36, 0.72)",
            "glass_strong": "rgba(23, 27, 36, 0.90)",
            "glass_border": "rgba(238, 242, 248, 0.10)",
            "scrim": "rgba(0, 0, 0, 0.45)",
        },
    }

    @staticmethod
    def mix(color_a, color_b, t):
        """Iki hex rengi t (0..1) oraninda karistirir.

        Hover gibi animasyonlu renk gecislerinde ara kareleri uretmek icin;
        yalnizca '#rrggbb' bicimindeki tokenlarla calisir (rgba degil).
        """
        t = max(0.0, min(1.0, float(t)))
        a = color_a.lstrip("#")
        b = color_b.lstrip("#")
        channels = (
            round(int(a[i:i + 2], 16) + (int(b[i:i + 2], 16) - int(a[i:i + 2], 16)) * t)
            for i in (0, 2, 4)
        )
        return "#{:02x}{:02x}{:02x}".format(*channels)

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
                background-color: {cls.text};
                color: {cls.bg};
                border: none;
                border-radius: 6px;
                padding: 6px 8px;
            }}
        """


Theme.configure("light")

