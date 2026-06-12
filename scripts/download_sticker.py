#!/usr/bin/env python3
"""Download a sticker from URL and save to stickers/ directory."""
import sys, os, urllib.request
from pathlib import Path

def download(url: str, name: str) -> str:
    """Download sticker and save with given name."""
    stickers_dir = Path(__file__).parent.parent / "stickers"
    ext = url.rsplit(".", 1)[-1].split("?")[0] or "png"
    path = stickers_dir / f"{name}.{ext}"
    urllib.request.urlretrieve(url, path)
    return str(path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download_sticker.py <url> <name>")
        sys.exit(1)
    result = download(sys.argv[1], sys.argv[2])
    print(f"✅ Saved: {result}")
