"""Archimedes — main GUI entry point."""

import math
import threading
import time
import tkinter.filedialog as filedialog
import webbrowser
from collections import Counter
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from .help_center import open_help_center
from .onboarding import show_welcome_if_needed
from .crypto_utils import PBKDF2_ITERATIONS, decrypt_message, encrypt_message
from .stego_core import extract_data, hide_data
from .ui_theme import (
    ACCENT,
    ACCENT_CRYPTO,
    AUTHOR_NAME,
    AUTHOR_URL,
    BG_CONSOLE,
    BG_INPUT,
    BG_PANEL,
    BG_ROOT,
    BOOT_LINES,
    BORDER,
    BORDER_WIDTH,
    BTN_COMMIT,
    BTN_EXTRACT,
    BTN_HELP,
    BTN_LOCATE,
    CORNER_RADIUS,
    CRYPTO_FINGERPRINT,
    DIALOG_HOST_OBJECT,
    FLAME_ART,
    FOOTER_PREFIX,
    HEADER_TAGLINE,
    LBL_ACCESS_TOKEN,
    LBL_DATA_FRAGMENT,
    LBL_HOST_OBJECT,
    LBL_OPS_CONSOLE,
    LBL_SECTION_OPS,
    LOG_TAG_COLORS,
    META_LINE,
    PH_ACCESS_TOKEN,
    PH_HOST_OBJECT,
    STATUS_LINE,
    STRIPE_COLOR,
    TEXT_BODY,
    TEXT_BRIGHT,
    TEXT_DIM,
    TITLE_SUB,
    TITLE_TEXT,
    WINDOW_TITLE,
    ghost_button_kwargs,
    load_fonts,
    outline_button_kwargs,
    primary_button_kwargs,
)

# Seconds between sequential log lines during background operations.
LOG_DELAY = 0.35


def _shannon_entropy(data: bytes) -> float:
    """Compute Shannon entropy in bits per byte (higher = more random/encrypted)."""
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def _panel_kwargs() -> dict:
    """Shared frame styling for terminal-style panels."""
    return {
        "fg_color": BG_PANEL,
        "border_color": BORDER,
        "border_width": BORDER_WIDTH,
        "corner_radius": CORNER_RADIUS,
    }


def _entry_kwargs() -> dict:
    """Shared entry field styling."""
    return {
        "fg_color": BG_INPUT,
        "border_color": BORDER,
        "text_color": TEXT_BODY,
        "placeholder_text_color": TEXT_DIM,
    }


def _textbox_kwargs() -> dict:
    """Shared textbox styling."""
    return {
        "fg_color": BG_INPUT,
        "border_color": BORDER,
        "text_color": TEXT_BODY,
    }


def _friendly_error(exc: Exception) -> str:
    """Map core exceptions to plain-language messages for the ops console."""
    if isinstance(exc, FileNotFoundError):
        return "That image file wasn't found. Use Browse to select a valid cover image."

    if isinstance(exc, OSError):
        return "Couldn't open that image. Try a PNG or JPG file."

    if isinstance(exc, ValueError):
        msg = str(exc)
        if "No hidden data found" in msg or "image is corrupted" in msg:
            return (
                "No hidden message found in this image. "
                "Make sure you're using a file created by Archimedes."
            )
        if "Incorrect password" in msg or "corrupted data" in msg:
            return "Wrong passphrase or corrupted image — decryption failed."
        if "Password cannot be empty" in msg:
            return "Enter your passphrase before continuing."
        if "Message cannot be empty" in msg:
            return "Type a message in the plaintext buffer before embedding."
        if "Payload too large" in msg:
            return (
                "Your message is too long for this cover image. "
                "Try a shorter message or use a larger image."
            )
        return msg

    return f"An unexpected error occurred: {exc}"


class ArchimedesApp(ctk.CTk):
    """Main application window for Archimedes steganography tool.

    Provides a GUI for:
    - Encrypting text with a passphrase (PBKDF2 + Fernet/AES-256)
    - Embedding the ciphertext into a cover image via LSB steganography
    - Extracting and decrypting hidden data from a stego image
    """

    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")

        self.configure(fg_color=BG_ROOT)
        self.title(WINDOW_TITLE)
        self.geometry("980x820")
        self.minsize(860, 740)

        self._fonts = load_fonts(self)
        self._busy = False
        self._build_layout()
        self._boot_sequence()
        self.after(100, lambda: show_welcome_if_needed(self, self._fonts))

    def _build_layout(self) -> None:
        """Construct the three main regions: header, controls panel, ops console."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Header ---
        header = ctk.CTkFrame(self, **_panel_kwargs())
        header.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")

        stripe = ctk.CTkFrame(header, height=3, fg_color=STRIPE_COLOR, corner_radius=0)
        stripe.pack(fill="x")

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="x", padx=20, pady=(18, 20))

        header_top = ctk.CTkFrame(header_inner, fg_color="transparent")
        header_top.pack(fill="x")

        self.help_btn = ctk.CTkButton(
            header_top,
            text=BTN_HELP,
            width=36,
            height=36,
            font=self._fonts["label"],
            command=self._open_help,
            **ghost_button_kwargs(),
        )
        self.help_btn.pack(side="right", anchor="ne")

        title_row = ctk.CTkFrame(header_inner, fg_color="transparent")
        title_row.pack(anchor="center")

        brand_row = ctk.CTkFrame(title_row, fg_color="transparent")
        brand_row.pack()

        ctk.CTkLabel(
            brand_row,
            text=FLAME_ART,
            font=self._fonts["flame"],
            text_color=ACCENT,
            justify="center",
        ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(
            brand_row,
            text=TITLE_TEXT,
            font=self._fonts["title"],
            text_color=TEXT_BRIGHT,
        ).pack(side="left")

        ctk.CTkLabel(
            title_row,
            text=TITLE_SUB,
            font=self._fonts["subtitle"],
            text_color=ACCENT,
        ).pack(pady=(10, 4))

        ctk.CTkLabel(
            title_row,
            text=META_LINE,
            font=self._fonts["label"],
            text_color=TEXT_BODY,
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            title_row,
            text=STATUS_LINE,
            font=self._fonts["section"],
            text_color=TEXT_DIM,
        ).pack(pady=(0, 3))

        ctk.CTkLabel(
            title_row,
            text=CRYPTO_FINGERPRINT,
            font=self._fonts["section"],
            text_color=ACCENT_CRYPTO,
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            title_row,
            text=HEADER_TAGLINE,
            font=self._fonts["section"],
            text_color=TEXT_DIM,
            justify="center",
            wraplength=720,
        ).pack(pady=(0, 4))

        # --- Controls panel ---
        controls = ctk.CTkFrame(self, **_panel_kwargs())
        controls.grid(row=1, column=0, padx=16, pady=8, sticky="ew")
        controls.grid_columnconfigure(1, weight=1)

        label_font = self._fonts["label"]
        mono_font = self._fonts["mono"]

        ctk.CTkLabel(
            controls,
            text=LBL_SECTION_OPS,
            font=label_font,
            text_color=ACCENT,
        ).grid(row=0, column=0, columnspan=3, padx=14, pady=(14, 6), sticky="w")

        ctk.CTkLabel(
            controls,
            text=LBL_HOST_OBJECT,
            font=label_font,
            text_color=TEXT_DIM,
        ).grid(row=1, column=0, padx=(14, 8), pady=(8, 8), sticky="w")

        self.target_entry = ctk.CTkEntry(
            controls,
            placeholder_text=PH_HOST_OBJECT,
            font=mono_font,
            height=36,
            **_entry_kwargs(),
        )
        self.target_entry.grid(row=1, column=1, padx=8, pady=(8, 8), sticky="ew")

        self.locate_btn = ctk.CTkButton(
            controls,
            text=BTN_LOCATE,
            width=110,
            height=36,
            font=mono_font,
            command=self._browse_target,
            **ghost_button_kwargs(),
        )
        self.locate_btn.grid(row=1, column=2, padx=(8, 14), pady=(8, 8))

        ctk.CTkLabel(
            controls,
            text=LBL_ACCESS_TOKEN,
            font=label_font,
            text_color=TEXT_DIM,
        ).grid(row=2, column=0, padx=(14, 8), pady=8, sticky="w")

        self.key_entry = ctk.CTkEntry(
            controls,
            show="*",
            placeholder_text=PH_ACCESS_TOKEN,
            font=mono_font,
            height=36,
            **_entry_kwargs(),
        )
        self.key_entry.grid(row=2, column=1, columnspan=2, padx=(8, 14), pady=8, sticky="ew")

        ctk.CTkLabel(
            controls,
            text=LBL_DATA_FRAGMENT,
            font=label_font,
            text_color=TEXT_DIM,
        ).grid(row=3, column=0, padx=(14, 8), pady=8, sticky="nw")

        self.payload_box = ctk.CTkTextbox(
            controls,
            height=110,
            font=mono_font,
            corner_radius=CORNER_RADIUS,
            **_textbox_kwargs(),
        )
        self.payload_box.grid(row=3, column=1, columnspan=2, padx=(8, 14), pady=8, sticky="ew")

        button_row = ctk.CTkFrame(controls, fg_color="transparent")
        button_row.grid(row=4, column=0, columnspan=3, padx=14, pady=(8, 14), sticky="ew")
        button_row.grid_columnconfigure((0, 1), weight=1)

        self.inject_btn = ctk.CTkButton(
            button_row,
            text=BTN_COMMIT,
            height=50,
            font=label_font,
            command=self._on_inject,
            **primary_button_kwargs(),
        )
        self.inject_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.parse_btn = ctk.CTkButton(
            button_row,
            text=BTN_EXTRACT,
            height=50,
            font=label_font,
            command=self._on_parse,
            **outline_button_kwargs(),
        )
        self.parse_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        # --- Ops console ---
        log_frame = ctk.CTkFrame(self, **_panel_kwargs())
        log_frame.grid(row=2, column=0, padx=16, pady=(8, 8), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            log_frame,
            text=LBL_OPS_CONSOLE,
            font=label_font,
            text_color=ACCENT,
        ).grid(row=0, column=0, padx=14, pady=(12, 4), sticky="w")

        self.log_box = ctk.CTkTextbox(
            log_frame,
            height=200,
            font=mono_font,
            state="disabled",
            wrap="word",
            fg_color=BG_CONSOLE,
            border_color=BORDER,
            text_color=TEXT_BODY,
            corner_radius=0,
        )
        self.log_box.grid(row=1, column=0, padx=14, pady=(4, 14), sticky="nsew")

        for level, color in LOG_TAG_COLORS.items():
            self.log_box.tag_config(level, foreground=color)

        # --- Footer ---
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, padx=16, pady=(0, 12), sticky="ew")

        footer_inner = ctk.CTkFrame(footer, fg_color="transparent")
        footer_inner.pack(anchor="center")

        ctk.CTkLabel(
            footer_inner,
            text=FOOTER_PREFIX,
            font=self._fonts["section"],
            text_color=TEXT_DIM,
        ).pack(side="left")

        author_link = ctk.CTkLabel(
            footer_inner,
            text=AUTHOR_NAME,
            font=self._fonts["section"],
            text_color=ACCENT,
            cursor="hand2",
        )
        author_link.pack(side="left")
        author_link.bind("<Button-1>", lambda _event: webbrowser.open(AUTHOR_URL))

    def _boot_sequence(self) -> None:
        """Emit the startup banner to the ops console."""
        for level, message in BOOT_LINES:
            self.log(level, message)

    def _open_help(self) -> None:
        """Open the in-app Help Center."""
        open_help_center(self, self._fonts, initial_tab="guide")

    def _browse_target(self) -> None:
        """Open a native file picker to select a cover image."""
        path = filedialog.askopenfilename(
            title=DIALOG_HOST_OBJECT,
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.target_entry.delete(0, "end")
            self.target_entry.insert(0, path)

    def log(self, level: str, message: str) -> None:
        """Append a timestamped, colour-coded line to the ops console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}\n"
        tag = level if level in LOG_TAG_COLORS else "INFO"

        def _append() -> None:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", line, tag)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")

        self.after(0, _append)

    def _set_busy(self, busy: bool) -> None:
        """Disable/enable action buttons while a background operation is running."""
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.inject_btn.configure(state=state)
        self.parse_btn.configure(state=state)

    def _get_target_path(self) -> str:
        return self.target_entry.get().strip()

    def _get_key(self) -> str:
        return self.key_entry.get()

    def _get_payload(self) -> str:
        return self.payload_box.get("1.0", "end").strip()

    def _set_payload(self, text: str) -> None:
        def _update() -> None:
            self.payload_box.delete("1.0", "end")
            self.payload_box.insert("1.0", text)

        self.after(0, _update)

    def _on_inject(self) -> None:
        if self._busy:
            return

        target = self._get_target_path()
        key = self._get_key()
        payload = self._get_payload()

        if not target or not key or not payload:
            self.log(
                "ERROR",
                "Choose a cover image, enter your passphrase, and type a message before embedding.",
            )
            return

        self._set_busy(True)
        threading.Thread(
            target=self._inject_worker,
            args=(target, key, payload),
            daemon=True,
        ).start()

    def _inject_worker(self, target: str, key: str, payload: str) -> None:
        """Background thread: encrypt the payload and embed it in the cover image."""
        try:
            self.log("CRYPTO", f"KDF::pbkdf2-sha256 ({PBKDF2_ITERATIONS:,} rounds)...")
            time.sleep(LOG_DELAY)

            self.log("CRYPTO", "fernet encrypt — AES-256-CBC + HMAC...")
            encrypted = encrypt_message(payload, key)

            entropy = _shannon_entropy(encrypted)
            self.log("CRYPTO", f"ciphertext entropy: {entropy:.2f} b/B")
            time.sleep(LOG_DELAY)

            target_path = Path(target)
            output_path = target_path.parent / f"{target_path.stem}_cipher.png"

            self.log("INFO", "embedding cipher into cover asset LSB plane...")
            hide_data(target, encrypted, str(output_path))

            self.log("SUCCESS", "ciphertext embedded — cover asset written.")
            self.log("INFO", f"output: {output_path}")
        except (FileNotFoundError, OSError, ValueError) as exc:
            self.log("ERROR", _friendly_error(exc))
        except Exception as exc:
            self.log("ERROR", _friendly_error(exc))
        finally:
            self.after(0, lambda: self._set_busy(False))

    def _on_parse(self) -> None:
        if self._busy:
            return

        target = self._get_target_path()
        key = self._get_key()

        if not target or not key:
            self.log(
                "ERROR",
                "Choose a cover image and enter your passphrase before recovering.",
            )
            return

        self._set_busy(True)
        threading.Thread(
            target=self._parse_worker,
            args=(target, key),
            daemon=True,
        ).start()

    def _parse_worker(self, target: str, key: str) -> None:
        """Background thread: extract the LSB payload and decrypt it."""
        try:
            self.log("INFO", "extracting LSB bitstream from cover asset...")
            time.sleep(LOG_DELAY)

            self.log("INFO", "scanning for payload terminator...")
            raw = extract_data(target)

            self.log("CRYPTO", f"ciphertext recovered ({len(raw)} bytes)")
            time.sleep(LOG_DELAY)

            self.log("CRYPTO", f"KDF::pbkdf2-sha256 ({PBKDF2_ITERATIONS:,} rounds)...")
            time.sleep(LOG_DELAY)

            self.log("CRYPTO", "fernet decrypt — verifying HMAC...")
            plaintext = decrypt_message(raw, key)

            self._set_payload(plaintext)
            self.log("SUCCESS", "plaintext recovered — HMAC verified.")
        except (FileNotFoundError, OSError, ValueError) as exc:
            self.log("ERROR", _friendly_error(exc))
        except Exception as exc:
            self.log("ERROR", _friendly_error(exc))
        finally:
            self.after(0, lambda: self._set_busy(False))


def main() -> None:
    """Entry point registered in pyproject.toml."""
    try:
        app = ArchimedesApp()
        app.mainloop()
    except Exception as exc:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Archimedes", f"Could not start the application.\n\n{exc}")
        root.destroy()


if __name__ == "__main__":
    main()
