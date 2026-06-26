"""First-run welcome modal for Archimedes."""

import customtkinter as ctk

from .help_center import open_help_center
from .preferences import is_welcome_dismissed, set_welcome_dismissed
from .ui_theme import (
    ACCENT,
    BG_PANEL,
    BG_ROOT,
    BORDER,
    BORDER_WIDTH,
    BTN_GET_STARTED,
    BTN_OPEN_GUIDE,
    CHK_DONT_SHOW_AGAIN,
    CORNER_RADIUS,
    DIALOG_WELCOME_TITLE,
    FLAME_ART,
    STRIPE_COLOR,
    TEXT_BODY,
    TEXT_BRIGHT,
    TEXT_DIM,
    TITLE_TEXT,
    WELCOME_HEIGHT,
    WELCOME_STEPS,
    WELCOME_TAGLINE,
    WELCOME_WIDTH,
    ghost_button_kwargs,
    primary_button_kwargs,
)


def _panel_kwargs() -> dict:
    return {
        "fg_color": BG_PANEL,
        "border_color": BORDER,
        "border_width": BORDER_WIDTH,
        "corner_radius": CORNER_RADIUS,
    }


class WelcomeDialog(ctk.CTkToplevel):
    """Modal welcome screen shown on first launch."""

    def __init__(self, parent: ctk.CTk, fonts: dict[str, tuple]) -> None:
        super().__init__(parent)

        self._parent = parent
        self._fonts = fonts
        self._dont_show_var = ctk.BooleanVar(value=True)

        self.title(DIALOG_WELCOME_TITLE)
        self.configure(fg_color=BG_ROOT)
        self.geometry(f"{WELCOME_WIDTH}x{WELCOME_HEIGHT}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._center_on_parent(parent)
        self._build_layout()

        self.protocol("WM_DELETE_WINDOW", self._dismiss)
        self.focus_force()

    def _center_on_parent(self, parent: ctk.CTk) -> None:
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - WELCOME_WIDTH) // 2
        py = parent.winfo_y() + (parent.winfo_height() - WELCOME_HEIGHT) // 2
        self.geometry(f"{WELCOME_WIDTH}x{WELCOME_HEIGHT}+{max(px, 0)}+{max(py, 0)}")

    def _build_layout(self) -> None:
        outer = ctk.CTkFrame(self, **_panel_kwargs())
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        stripe = ctk.CTkFrame(outer, height=3, fg_color=STRIPE_COLOR, corner_radius=0)
        stripe.pack(fill="x")

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=(20, 22))

        brand_row = ctk.CTkFrame(inner, fg_color="transparent")
        brand_row.pack()

        ctk.CTkLabel(
            brand_row,
            text=FLAME_ART,
            font=self._fonts["flame"],
            text_color=ACCENT,
            justify="center",
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            brand_row,
            text=TITLE_TEXT,
            font=self._fonts["title"],
            text_color=TEXT_BRIGHT,
        ).pack(side="left")

        ctk.CTkLabel(
            inner,
            text=WELCOME_TAGLINE,
            font=self._fonts["subtitle"],
            text_color=TEXT_BODY,
            wraplength=WELCOME_WIDTH - 80,
            justify="center",
        ).pack(pady=(18, 20))

        steps_frame = ctk.CTkFrame(inner, fg_color=BG_ROOT, border_color=BORDER, border_width=1)
        steps_frame.pack(fill="x", pady=(0, 18))

        for idx, (num, title, detail) in enumerate(WELCOME_STEPS):
            row = ctk.CTkFrame(steps_frame, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=(12 if idx == 0 else 4, 12 if idx == len(WELCOME_STEPS) - 1 else 4))

            ctk.CTkLabel(
                row,
                text=num,
                font=self._fonts["label"],
                text_color=ACCENT,
                width=24,
            ).pack(side="left", anchor="n")

            text_col = ctk.CTkFrame(row, fg_color="transparent")
            text_col.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                text_col,
                text=title,
                font=self._fonts["label"],
                text_color=TEXT_BRIGHT,
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_col,
                text=detail,
                font=self._fonts["section"],
                text_color=TEXT_DIM,
                wraplength=WELCOME_WIDTH - 120,
                justify="left",
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))

        ctk.CTkCheckBox(
            inner,
            text=CHK_DONT_SHOW_AGAIN,
            variable=self._dont_show_var,
            font=self._fonts["section"],
            text_color=TEXT_DIM,
            fg_color=ACCENT,
            hover_color=ACCENT,
            border_color=BORDER,
        ).pack(anchor="w", pady=(0, 14))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row,
            text=BTN_OPEN_GUIDE,
            height=40,
            font=self._fonts["section"],
            command=self._open_guide,
            **ghost_button_kwargs(),
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text=BTN_GET_STARTED,
            height=40,
            width=140,
            font=self._fonts["label"],
            command=self._dismiss,
            **primary_button_kwargs(),
        ).pack(side="right")

    def _open_guide(self) -> None:
        open_help_center(self._parent, self._fonts, initial_tab="guide")

    def _dismiss(self) -> None:
        if self._dont_show_var.get():
            set_welcome_dismissed(True)
        self.grab_release()
        self.destroy()


def show_welcome_if_needed(parent: ctk.CTk, fonts: dict[str, tuple]) -> None:
    """Show the welcome modal on first launch unless previously dismissed."""
    if not is_welcome_dismissed():
        WelcomeDialog(parent, fonts)
