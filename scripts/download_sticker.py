#!/usr/bin/env python3
"""Download a sticker from URL and save to stickers/ directory."""
import sys
import urllib.request
import urllib.error
import socket
from pathlib import Path
from urllib.parse import urlparse

def download(url, name):
    """Download sticker and save with given name. Returns path or None."""
    try:
        stickers_dir = Path(__file__).parent.parent / "stickers"

        # Determine extension from URL path
        parsed = urlparse(url)
        path_part = parsed.path
        if "." in path_part:
            ext = path_part.rsplit(".", 1)[-1].split("?")[0]
            if len(ext) > 5 or ext.lower() not in ("png", "jpg", "jpeg", "gif", "webp", "bmp"):
                ext = "png"
        else:
            ext = "png"

        filepath = stickers_dir / f"{name}.{ext}"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()

        if len(data) < 1024:
            print(f"⚠️ 下载文件太小 ({len(data)}B)", file=sys.stderr)
            return None

        filepath.write_bytes(data)
        return str(filepath)

    except (urllib.error.URLError, socket.timeout) as e:
        print(f"⚠️ 网络错误: {e}", file=sys.stderr)
    except OSError as e:
        print(f"⚠️ 文件写入失败: {e}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ 下载失败: {e}", file=sys.stderr)

    return None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download_sticker.py <url> <name>")
        sys.exit(1)
    result = download(sys.argv[1], sys.argv[2])
    if result:
        print(f"✅ Saved: {result}")
    else:
        sys.exit(1)
