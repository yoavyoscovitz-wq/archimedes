"""In-app Help Center — static guide and FAQ content plus dialog UI."""

import webbrowser

import customtkinter as ctk

from .ui_theme import (
    ACCENT,
    BG_CONSOLE,
    BG_PANEL,
    BG_ROOT,
    BORDER,
    BORDER_WIDTH,
    BTN_GITHUB_DOCS,
    BTN_OUTLINE_HOVER,
    CORNER_RADIUS,
    HELP_HEIGHT,
    HELP_WIDTH,
    LBL_HELP_FAQ,
    LBL_HELP_GUIDE,
    LBL_HELP_TITLE,
    REPO_URL,
    STRIPE_COLOR,
    TEXT_BODY,
    TEXT_BRIGHT,
    TEXT_DIM,
    ghost_button_kwargs,
    outline_button_kwargs,
    primary_button_kwargs,
)

GUIDE_TEXT = """\
HOW TO USE ARCHIMEDES
═══════════════════════════════════════════════════════════════

BEFORE YOU START
────────────────
  • Python 3.10 or later and pip
  • Clone the repository from GitHub
  • Create a virtual environment (recommended)
  • Install: pip install -e .
  • Launch: archimedes

  Windows (PowerShell):
    python -m venv .venv
    .venv\\Scripts\\activate
    pip install -e .
    archimedes

  macOS / Linux:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
    archimedes


NO SETUP REQUIRED
─────────────────
  • No API keys, accounts, or environment variables
  • No network connection — everything runs on your machine
  • Your passphrase is the only secret; it is never stored on disk


ENC · EMBED — Hide a message
────────────────────────────
  1. Click BROWSE and select a cover image (PNG or JPG works best)
  2. Enter your passphrase in the Passphrase field
  3. Type your secret message in Plaintext Buffer
  4. Click ENC · EMBED

  Output: a new file named {original}_cipher.png is saved in the
  same folder as your cover image. The image looks identical to the
  original — the hidden data lives in invisible pixel changes.


DEC · RECOVER — Read a hidden message
─────────────────────────────────────
  1. Click BROWSE and select the cipher image (*_cipher.png)
  2. Enter the same passphrase you used when embedding
  3. Click DEC · RECOVER

  Your original message appears in Plaintext Buffer. Check the
  Output Log at the bottom for step-by-step status.


TIPS
────
  • Use PNG cover images for best reliability
  • Keep your passphrase safe — there is no recovery if you lose it
  • Do not re-compress or edit cipher images in other apps; that can
    destroy the hidden data
  • Watch the Output Log for clear error messages if something fails
  • Press ? in the header anytime to reopen this guide
"""

FAQ_TEXT = """\
FREQUENTLY ASKED QUESTIONS
═══════════════════════════════════════════════════════════════

Do I need API keys or an account?
──────────────────────────────────
  No. Archimedes is fully offline. There are no API keys, logins,
  or cloud services. Install locally and run.


What image formats are supported?
─────────────────────────────────
  PNG, JPG, JPEG, and BMP. PNG is recommended for embedding because
  lossless formats preserve the hidden LSB data more reliably.


Where is my output saved?
─────────────────────────
  Next to your original cover image, with _cipher appended to the
  filename. Example: photo.jpg → photo_cipher.png


Will the image look different?
──────────────────────────────
  No visible change. Archimedes modifies only the least significant
  bit of each colour channel — a change the human eye cannot see.


I forgot my passphrase. Can I recover the message?
──────────────────────────────────────────────────
  No. Without the correct passphrase, the encrypted data cannot be
  decrypted. This is by design.


I get "Wrong passphrase or corrupted image."
────────────────────────────────────────────
  The passphrase does not match what was used during embedding, or
  the file was altered. Double-check the passphrase and ensure you
  selected the correct cipher image.


I get "No hidden message found in this image."
──────────────────────────────────────────────
  The file was not created by Archimedes, or the hidden data was
  destroyed (e.g. by re-saving as JPEG, cropping, or filtering).


Is this safe for sensitive production use?
──────────────────────────────────────────
  Archimedes is an open-source educational and portfolio project.
  Review the Legal Disclaimer in the GitHub README before relying
  on it for high-stakes scenarios.


How do I see the welcome screen again?
──────────────────────────────────────
  Delete the config file at ~/.archimedes/config.json (or
  %USERPROFILE%\\.archimedes\\config.json on Windows), then restart
  the app.


Where can I get more help?
──────────────────────────
  Click "Full docs on GitHub" below, or open an issue on the
  project repository.
"""


def _panel_kwargs() -> dict:
    return {
        "fg_color": BG_PANEL,
        "border_color": BORDER,
        "border_width": BORDER_WIDTH,
        "corner_radius": CORNER_RADIUS,
    }


class HelpCenterDialog(ctk.CTkToplevel):
    """Tabbed help dialog with Guide and FAQ sections."""

    def __init__(
        self,
        parent: ctk.CTk,
        fonts: dict[str, tuple],
        initial_tab: str = "guide",
    ) -> None:
        super().__init__(parent)

        self._fonts = fonts
        self._active_tab = initial_tab

        self.title(LBL_HELP_TITLE)
        self.configure(fg_color=BG_ROOT)
        self.geometry(f"{HELP_WIDTH}x{HELP_HEIGHT}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._center_on_parent(parent)
        self._build_layout()
        self._show_tab(initial_tab)

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.focus_force()

    def _center_on_parent(self, parent: ctk.CTk) -> None:
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width() - HELP_WIDTH) // 2
        py = parent.winfo_y() + (parent.winfo_height() - HELP_HEIGHT) // 2
        self.geometry(f"{HELP_WIDTH}x{HELP_HEIGHT}+{max(px, 0)}+{max(py, 0)}")

    def _build_layout(self) -> None:
        outer = ctk.CTkFrame(self, **_panel_kwargs())
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        stripe = ctk.CTkFrame(outer, height=3, fg_color=STRIPE_COLOR, corner_radius=0)
        stripe.pack(fill="x")

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=(16, 20))

        ctk.CTkLabel(
            inner,
            text=LBL_HELP_TITLE,
            font=self._fonts["label"],
            text_color=TEXT_BRIGHT,
        ).pack(anchor="w", pady=(0, 12))

        tab_row = ctk.CTkFrame(inner, fg_color="transparent")
        tab_row.pack(fill="x", pady=(0, 10))

        self._guide_tab_btn = ctk.CTkButton(
            tab_row,
            text=LBL_HELP_GUIDE,
            height=34,
            font=self._fonts["section"],
            command=lambda: self._show_tab("guide"),
            **outline_button_kwargs(),
        )
        self._guide_tab_btn.pack(side="left", padx=(0, 8))

        self._faq_tab_btn = ctk.CTkButton(
            tab_row,
            text=LBL_HELP_FAQ,
            height=34,
            font=self._fonts["section"],
            command=lambda: self._show_tab("faq"),
            **ghost_button_kwargs(),
        )
        self._faq_tab_btn.pack(side="left")

        self.content_box = ctk.CTkTextbox(
            inner,
            font=self._fonts["mono"],
            wrap="word",
            fg_color=BG_CONSOLE,
            border_color=BORDER,
            text_color=TEXT_BODY,
            corner_radius=0,
        )
        self.content_box.pack(fill="both", expand=True, pady=(0, 12))

        footer = ctk.CTkFrame(inner, fg_color="transparent")
        footer.pack(fill="x")

        ctk.CTkButton(
            footer,
            text=BTN_GITHUB_DOCS,
            height=36,
            font=self._fonts["section"],
            command=lambda: webbrowser.open(REPO_URL),
            **ghost_button_kwargs(),
        ).pack(side="left")

        ctk.CTkButton(
            footer,
            text="Close",
            width=90,
            height=36,
            font=self._fonts["section"],
            command=self._close,
            **primary_button_kwargs(),
        ).pack(side="right")

    def _show_tab(self, tab: str) -> None:
        self._active_tab = tab
        text = GUIDE_TEXT if tab == "guide" else FAQ_TEXT
        self.content_box.configure(state="normal")
        self.content_box.delete("1.0", "end")
        self.content_box.insert("1.0", text)
        self.content_box.configure(state="disabled")

        if tab == "guide":
            self._guide_tab_btn.configure(
                border_color=ACCENT,
                text_color=TEXT_BRIGHT,
                fg_color=BTN_OUTLINE_HOVER,
            )
            self._faq_tab_btn.configure(**ghost_button_kwargs())
        else:
            self._faq_tab_btn.configure(
                border_color=ACCENT,
                text_color=TEXT_BRIGHT,
                fg_color=BTN_OUTLINE_HOVER,
            )
            self._guide_tab_btn.configure(**ghost_button_kwargs())

    def _close(self) -> None:
        self.grab_release()
        self.destroy()


def open_help_center(
    parent: ctk.CTk,
    fonts: dict[str, tuple],
    initial_tab: str = "guide",
) -> HelpCenterDialog:
    """Open the Help Center dialog on top of the main window."""
    return HelpCenterDialog(parent, fonts, initial_tab=initial_tab)
