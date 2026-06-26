"""Visual theme constants and widget helper functions for the Archimedes GUI."""

from pathlib import Path

import tkinter

# ---------------------------------------------------------------------------
# Colour palette — dark terminal aesthetic
# ---------------------------------------------------------------------------
BG_ROOT = "#0D0D0D"
BG_PANEL = "#1A1A1A"
BG_CONSOLE = "#080808"
BG_INPUT = "#141414"
BORDER = "#2E2E2E"
BORDER_HI = "#3A5A7A"
TEXT_DIM = "#7A7A7A"
TEXT_BODY = "#DCDCDC"
TEXT_BRIGHT = "#FFFFFF"
ACCENT = "#1B8ADB"
ACCENT_HI = "#3DA5E8"
ACCENT_CRYPTO = "#5CB8FF"
ACCENT_AMBER = "#E8A838"
ACCENT_WARN = "#E8A838"
ACCENT_ERR = "#E05252"
ACCENT_OK = "#4FC3A1"

BTN_PRIMARY_BG = "#1565A8"
BTN_PRIMARY_HOVER = "#1B8ADB"
BTN_PRIMARY_TEXT = "#FFFFFF"
BTN_GHOST_BG = "#1A1A1A"
BTN_GHOST_HOVER = "#252525"
BTN_GHOST_BORDER = "#3A3A3A"
BTN_GHOST_TEXT = "#AAAAAA"
BTN_OUTLINE_BORDER = "#1B8ADB"
BTN_OUTLINE_HOVER = "#122A3D"

CORNER_RADIUS = 4
BORDER_WIDTH = 1
STRIPE_COLOR = "#1B8ADB"

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
MONO_FAMILY = "Consolas"
MONO_SIZE = 14
LABEL_SIZE = 15
TITLE_SIZE = 58
FLAME_SIZE = 30
SECTION_SIZE = 13
SUBTITLE_SIZE = 14

def _resolve_font_path() -> Path:
    """Locate bundled VT323 font (installed package or dev source tree)."""
    candidates = [
        Path(__file__).resolve().parent / "assets" / "fonts" / "VT323-Regular.ttf",
        Path(__file__).resolve().parent.parent.parent / "assets" / "fonts" / "VT323-Regular.ttf",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return candidates[-1]


FONT_PATH = _resolve_font_path()

# ---------------------------------------------------------------------------
# Branding strings
# ---------------------------------------------------------------------------
WINDOW_TITLE = "ARCHIMEDES — local steganography tool"
TITLE_TEXT = "ARCHIMEDES"
TITLE_SUB = "──  local encryption & steganography  ──"
META_LINE = "All processing runs on your machine. Nothing is sent over the network."
STATUS_LINE = "Ready — select a cover image and enter your passphrase."
CRYPTO_FINGERPRINT = "PBKDF2-SHA256 key derivation  ·  Fernet (AES-256)  ·  LSB image embedding"

HEADER_TAGLINE = (
    "Encrypt text with your passphrase and hide it inside an image — "
    "invisible to the eye, recoverable with the same key."
)

TOOL_ABOUT = (
    "Archimedes encrypts a text message with your passphrase, then hides the\n"
    "ciphertext inside an image using least-significant-bit (LSB) steganography.\n"
    "DEC · RECOVER reads the hidden bytes from a cover image and decrypts them\n"
    "with the same passphrase. Output images are saved locally as PNG files."
)

WELCOME_TAGLINE = (
    "Encrypt a secret message, hide it inside an ordinary image, and share the "
    "photo openly—your data stays invisible in plain sight."
)

WELCOME_STEPS = [
    ("1", "Install", "Clone the repo, run pip install -e ., then launch archimedes."),
    ("2", "Embed", "Pick a cover image, enter a passphrase, type your message, and click ENC · EMBED."),
    ("3", "Recover", "Open the cipher image, enter the same passphrase, and click DEC · RECOVER."),
]

FLAME_ART = " ▄▄▄\n ████▄\n  ▀███▄\n   ▀▀"

AUTHOR_NAME = "Yoav Yoscovitz"
AUTHOR_URL = "https://github.com/yoavyoscovitz-wq"
REPO_URL = "https://github.com/yoavyoscovitz-wq/archimedes"
FOOTER_PREFIX = "Created by "

# Onboarding / help dialogs
WELCOME_WIDTH = 520
WELCOME_HEIGHT = 480
HELP_WIDTH = 620
HELP_HEIGHT = 520
BTN_HELP = "?"
BTN_GET_STARTED = "Get Started"
BTN_OPEN_GUIDE = "Open full guide"
BTN_GITHUB_DOCS = "Full docs on GitHub"
CHK_DONT_SHOW_AGAIN = "Don't show this again"
LBL_HELP_TITLE = "Help Center"
LBL_HELP_GUIDE = "How to Use"
LBL_HELP_FAQ = "FAQ"
DIALOG_WELCOME_TITLE = "Welcome to Archimedes"

# ---------------------------------------------------------------------------
# Surface labels
# ---------------------------------------------------------------------------
LBL_SECTION_OPS = "▸  CRYPTO PIPELINE"
LBL_HOST_OBJECT = "Cover Asset"
LBL_ACCESS_TOKEN = "Passphrase"
LBL_DATA_FRAGMENT = "Plaintext Buffer"
LBL_OPS_CONSOLE = "▸  OUTPUT LOG"

PH_HOST_OBJECT = "Browse or paste a PNG/JPG path..."
PH_ACCESS_TOKEN = "Enter your passphrase..."

BTN_LOCATE = "BROWSE"
BTN_COMMIT = "ENC  ·  EMBED"
BTN_EXTRACT = "DEC  ·  RECOVER"

DIALOG_HOST_OBJECT = "Select Cover Asset"

# ---------------------------------------------------------------------------
# Log level → colour mapping
# ---------------------------------------------------------------------------
LOG_TAG_COLORS = {
    "INFO": ACCENT_CRYPTO,
    "SUCCESS": ACCENT_OK,
    "ERROR": ACCENT_ERR,
    "SYS": TEXT_DIM,
    "CRYPTO": ACCENT_AMBER,
}

BOOT_LINES = [
    ("SYS", "Archimedes ready — local steganography engine"),
    ("SYS", "ENC · EMBED: encrypt text and hide it in a cover image"),
    ("SYS", "DEC · RECOVER: extract and decrypt hidden data from an image"),
]


def load_fonts(root) -> dict[str, tuple]:
    """Register the bundled VT323 pixel font and return CTk-compatible font tuples."""
    pixel_family = MONO_FAMILY
    if FONT_PATH.is_file():
        try:
            root.tk.call("font", "create", "VT323Archimedes", "-file", str(FONT_PATH))
            pixel_family = "VT323Archimedes"
        except tkinter.TclError:
            pass

    return {
        "mono": (MONO_FAMILY, MONO_SIZE),
        "label": (MONO_FAMILY, LABEL_SIZE),
        "section": (MONO_FAMILY, SECTION_SIZE),
        "subtitle": (MONO_FAMILY, SUBTITLE_SIZE),
        "title": (pixel_family, TITLE_SIZE),
        "flame": (pixel_family, FLAME_SIZE),
    }


def primary_button_kwargs() -> dict:
    """Style kwargs for the primary action button."""
    return {
        "fg_color": BTN_PRIMARY_BG,
        "hover_color": BTN_PRIMARY_HOVER,
        "text_color": BTN_PRIMARY_TEXT,
        "border_width": 0,
        "corner_radius": CORNER_RADIUS,
    }


def ghost_button_kwargs() -> dict:
    """Style kwargs for secondary utility buttons."""
    return {
        "fg_color": BTN_GHOST_BG,
        "hover_color": BTN_GHOST_HOVER,
        "border_color": BTN_GHOST_BORDER,
        "border_width": 1,
        "text_color": BTN_GHOST_TEXT,
        "corner_radius": CORNER_RADIUS,
    }


def outline_button_kwargs() -> dict:
    """Style kwargs for outlined secondary action buttons."""
    return {
        "fg_color": BTN_GHOST_BG,
        "hover_color": BTN_OUTLINE_HOVER,
        "border_color": BTN_OUTLINE_BORDER,
        "border_width": 1,
        "text_color": ACCENT_HI,
        "corner_radius": CORNER_RADIUS,
    }
