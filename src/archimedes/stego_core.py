"""LSB steganography — hide and extract binary data inside PNG images."""

import sys
import tempfile
from pathlib import Path

from PIL import Image

# Sentinel appended after the payload so extraction knows where data ends.
END_MARKER = b"<END_OF_DATA>"


def _bytes_to_bits(data: bytes) -> str:
    """Convert bytes to a contiguous binary string (MSB-first per byte)."""
    return "".join(f"{byte:08b}" for byte in data)


def _bits_to_bytes(bits: str) -> bytes:
    """Convert a binary string to bytes, discarding trailing incomplete octets."""
    complete_bits = bits[: len(bits) - (len(bits) % 8)]
    return bytes(int(complete_bits[i : i + 8], 2) for i in range(0, len(complete_bits), 8))


def _get_lsb(channel: int) -> int:
    """Return the least significant bit of a colour channel value."""
    return channel & 1


def _set_lsb(channel: int, bit: int) -> int:
    """Set the least significant bit of a colour channel value without touching other bits."""
    return (channel & 0xFE) | (bit & 1)


def _image_capacity_bits(img: Image.Image) -> int:
    """Return the total number of embeddable bits (one per RGB channel per pixel)."""
    return img.width * img.height * 3


def hide_data(image_path: str, data: bytes, output_path: str) -> None:
    """Embed binary data into the LSBs of an RGB image and save the result as PNG.

    Each byte of ``data`` (plus the END_MARKER sentinel) is spread across the
    least significant bit of each R, G, B channel in raster order.  The change
    is visually imperceptible.

    Raises:
        FileNotFoundError: if ``image_path`` does not exist.
        OSError: if the image cannot be opened.
        ValueError: if the payload is too large for the cover image.
    """
    cover_path = Path(image_path)
    if not cover_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    try:
        img = Image.open(cover_path).convert("RGB")
    except OSError as exc:
        raise OSError(f"Unable to read image: {image_path}") from exc

    payload = data + END_MARKER
    bits = _bytes_to_bits(payload)
    capacity = _image_capacity_bits(img)

    if len(bits) > capacity:
        required_bytes = (len(bits) + 7) // 8
        available_bytes = capacity // 8
        raise ValueError(
            f"Payload too large: needs {len(bits)} bits ({required_bytes} bytes), "
            f"but image supports {capacity} bits ({available_bytes} bytes)."
        )

    pixels = img.load()
    bit_index = 0

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            channels = [r, g, b]

            for channel_idx in range(3):
                if bit_index >= len(bits):
                    pixels[x, y] = tuple(channels)
                    img.save(output_path, "PNG")
                    return

                channels[channel_idx] = _set_lsb(channels[channel_idx], int(bits[bit_index]))
                bit_index += 1

            pixels[x, y] = tuple(channels)

    img.save(output_path, "PNG")


def extract_data(image_path: str) -> bytes:
    """Extract hidden binary data from the LSBs of an RGB image.

    Reads the LSB of each R, G, B channel in raster order and reassembles
    bytes until the END_MARKER sentinel is found.

    Raises:
        FileNotFoundError: if ``image_path`` does not exist.
        OSError: if the image cannot be opened.
        ValueError: if no END_MARKER is found (image has no hidden data).
    """
    cover_path = Path(image_path)
    if not cover_path.is_file():
        raise FileNotFoundError(f"Image not found: {image_path}")

    try:
        img = Image.open(cover_path).convert("RGB")
    except OSError as exc:
        raise OSError(f"Unable to read image: {image_path}") from exc

    pixels = img.load()
    bits = ""

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            for channel in (r, g, b):
                bits += str(_get_lsb(channel))
                extracted = _bits_to_bytes(bits)
                if extracted.endswith(END_MARKER):
                    return extracted[: -len(END_MARKER)]

    raise ValueError("No hidden data found or image is corrupted.")


if __name__ == "__main__":
    _secret = b"Archimedes LSB steganography test payload"

    try:
        with tempfile.TemporaryDirectory() as _tmp:
            _cover = Path(_tmp) / "cover.png"
            _stego = Path(_tmp) / "stego.png"

            _img = Image.new("RGB", (100, 100))
            _px = _img.load()
            for _y in range(100):
                for _x in range(100):
                    _px[_x, _y] = (_x % 256, _y % 256, (_x + _y) % 256)
            _img.save(_cover, "PNG")

            hide_data(str(_cover), _secret, str(_stego))
            _extracted = extract_data(str(_stego))
            assert _extracted == _secret, "Round-trip mismatch"

        print("[PASS] Round-trip hide/extract")
        print("All tests passed.")
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] {exc}")
        sys.exit(1)
