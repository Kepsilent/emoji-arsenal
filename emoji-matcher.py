#!/usr/bin/env python3
"""Emoji Arsenal — Smart sticker matcher for OpenClaw.

Matches user messages to stickers using keyword + emotion detection.
Supports local cache with automatic web search fallback.
Features diversity rotation, smart caching with tier promotion/demotion.

Usage:
    python emoji-matcher.py "好开心啊哈哈哈哈"
    → {"emotion": "happy", "path": "stickers/开心_咧嘴笑.png", "source": "local"}

Requirements:
    pip install jieba
"""

import json
import os
import re
import sys
import time
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta

try:
    import jieba
except ImportError:
    jieba = None

SKILL_DIR = Path(__file__).parent.resolve()
INDEX_PATH = SKILL_DIR / "stickers" / "index.json"
USAGE_PATH = SKILL_DIR / "stickers" / "usage.json"
STICKERS_DIR = SKILL_DIR / "stickers"

EMOTIONS = {
    "happy":     ["开心", "哈哈", "笑嘻嘻", "高兴", "快乐", "兴奋", "嘻嘻"],
    "sad":       ["难过", "哭泣", "伤心", "呜呜", "emo", "哭"],
    "love":      ["爱你", "亲亲", "比心", "喜欢", "么么哒", "爱", "❤", "💕"],
    "angry":     ["生气", "愤怒", "烦死了", "无语", "气"],
    "surprise":  ["震惊", "卧槽", "天哪", "不会吧"],
    "cute":      ["可爱", "卖萌", "害羞"],
    "approve":   ["点赞", "棒", "牛", "厉害", "666", "赞"],
    "goodbye":   ["拜拜", "晚安", "再见", "溜了"],
    "laugh":     ["笑死", "笑cry", "🤣", "😂", "哈哈哈哈"],
}

STICKER_STYLES = {
    "cute":           "可爱 卡通 萌",
    "funny":          "搞笑 幽默 滑稽",
    "angry_style":    "生气 暴躁 发怒",
    "surprise_style": "惊讶 震惊 目瞪口呆",
    "sweet":          "甜蜜 温馨 暖心",
}

EMOTION_STYLE = {
    "happy": "cute", "sad": "cute", "love": "sweet",
    "angry": "angry_style", "surprise": "surprise_style",
    "cute": "cute", "approve": "cute", "goodbye": "cute", "laugh": "funny",
}

EMOTION_DESC = {
    "happy": "开心快乐的表情包，笑容灿烂",
    "sad": "难过哭泣的表情包，委屈巴巴",
    "love": "爱心表达的表情包，甜蜜温馨",
    "angry": "生气愤怒的表情包，暴躁抓狂",
    "surprise": "惊讶震惊的表情包，目瞪口呆",
    "cute": "可爱卖萌的表情包，萌化了",
    "approve": "点赞赞同的表情包，太棒了",
    "goodbye": "再见告别的表情包，下次见",
    "laugh": "爆笑搞笑的表情包，笑死了",
}

PROMOTION_THRESHOLD = 3
HOT_EXPIRY_DAYS = 60
TEMP_EXPIRY_DAYS = 30
CLEANUP_INTERVAL_DAYS = 30

def load_json(path):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def save_json(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def detect_emotion(text):
    text_lower = text.lower()
    scores = {}
    for emotion, keywords in EMOTIONS.items():
        score = 0
        for kw in keywords:
            if kw.lower() in text_lower:
                score += len(kw)
        if score > 0:
            scores[emotion] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def get_sticker_files(index, emotion):
    entries = index.get(emotion, [])
    if not entries:
        return []
    if isinstance(entries[0], dict):
        return entries
    return [{"file": f, "description": "", "style": "auto"}
            for f in entries if isinstance(f, str)]

def search_local(emotion):
    """Search local stickers with diversity rotation (pick least-used first)."""
    index = load_json(INDEX_PATH)
    usage = load_json(USAGE_PATH)
    files_meta = get_sticker_files(index, emotion)
    if not files_meta:
        return None

    files_data = usage.get("files", {})
    available = []

    for meta in files_meta:
        fname = meta["file"]
        full_path = STICKERS_DIR / fname
        if full_path.exists():
            finfo = files_data.get(fname, {})
            count = finfo.get("count", 0) if isinstance(finfo, dict) else 0
            available.append((count, meta, full_path))

    if not available:
        return None

    available.sort(key=lambda x: x[0])
    _, chosen_meta, chosen_path = available[0]

    return {
        "file": chosen_meta["file"],
        "path": str(chosen_path),
        "description": chosen_meta.get("description", ""),
        "style": chosen_meta.get("style", "auto"),
    }


def update_usage(emotion, filename=None):
    """Increment usage counter and manage tier promotion."""
    usage = load_json(USAGE_PATH)
    now = time.strftime("%Y-%m-%dT%H:%M:%S")

    if emotion not in usage or not isinstance(usage[emotion], dict):
        usage[emotion] = {"count": 0, "last_used": "", "tier": "temporary"}
    emo = usage[emotion]
    emo["count"] = emo.get("count", 0) + 1
    emo["last_used"] = now
    if emo["count"] >= PROMOTION_THRESHOLD and emo.get("tier", "temporary") == "temporary":
        emo["tier"] = "hot"
        print(f"⭐ [{emotion}] 升级为常用情绪 (计数: {emo['count']})", file=sys.stderr)

    if filename:
        files = usage.setdefault("files", {})
        if filename not in files or not isinstance(files[filename], dict):
            files[filename] = {"count": 0, "last_used": "", "tier": "temporary"}
        finfo = files[filename]
        finfo["count"] = finfo.get("count", 0) + 1
        finfo["last_used"] = now
        if finfo["count"] >= PROMOTION_THRESHOLD and finfo.get("tier", "temporary") == "temporary":
            finfo["tier"] = "hot"
            print(f"⭐ [{filename}] 升级为常用表情 (计数: {finfo['count']})", file=sys.stderr)

    usage["_last_updated"] = now
    save_json(USAGE_PATH, usage)

def needs_cleanup():
    usage = load_json(USAGE_PATH)
    last_cleanup = usage.get("_last_cleanup", "")
    if not last_cleanup:
        return True
    try:
        last = datetime.strptime(last_cleanup, "%Y-%m-%d")
        return (datetime.now() - last).days >= CLEANUP_INTERVAL_DAYS
    except ValueError:
        return True


def cleanup_cache(force=False):
    """Clean up old stickers based on tier rules."""
    if not force and not needs_cleanup():
        return []

    usage = load_json(USAGE_PATH)
    index = load_json(INDEX_PATH)
    now = datetime.now()
    deleted = []
    files_data = usage.get("files", {})

    for fname, finfo in list(files_data.items()):
        if not isinstance(finfo, dict):
            continue

        last_used_str = finfo.get("last_used", "")
        tier = finfo.get("tier", "temporary")
        if not last_used_str:
            continue

        if tier == "bundle":
            continue

        try:
            last_used = datetime.strptime(last_used_str.split("T")[0], "%Y-%m-%d")
        except ValueError:
            continue

        days_since = (now - last_used).days

        if tier == "hot":
            if days_since >= HOT_EXPIRY_DAYS:
                finfo["tier"] = "temporary"
                print(f"⬇ [{fname}] 热度过期降级 ({days_since}天未用)", file=sys.stderr)
        elif tier == "temporary":
            if days_since >= TEMP_EXPIRY_DAYS:
                file_path = STICKERS_DIR / fname
                if file_path.exists():
                    file_path.unlink()
                    deleted.append(fname)
                    print(f"🗑 [{fname}] 已清理 ({days_since}天未用)", file=sys.stderr)

                for emotion in list(index.keys()):
                    entries = index[emotion]
                    if isinstance(entries, list):
                        index[emotion] = [
                            e for e in entries
                            if not (isinstance(e, dict) and e.get("file") == fname)
                            and not (isinstance(e, str) and e == fname)
                        ]
                del files_data[fname]

    usage["files"] = files_data
    usage["_last_cleanup"] = now.strftime("%Y-%m-%d")
    save_json(USAGE_PATH, usage)
    save_json(INDEX_PATH, index)
    return deleted

def search_web(query, style="cute"):
    """Search Baidu image search. Returns first image URL or None."""
    style_suffix = STICKER_STYLES.get(style, "表情包")
    search_query = f"{query} {style_suffix}"
    encoded = urllib.parse.quote(search_query)
    url = f"https://image.baidu.com/search?word={encoded}&tn=baiduimage"

    try:
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
            html = resp.read().decode("utf-8", errors="replace")

        for pattern in [
            r'"thumbURL":"(https?://[^"]+)"',
            r'"objURL":"(https?://[^"]+)"',
            r'"middleURL":"(https?://[^"]+)"',
        ]:
            urls = re.findall(pattern, html)
            if urls:
                return urls[0]

    except Exception as e:
        print(f"⚠️ 联网搜索失败: {e}", file=sys.stderr)

    return None


def download_sticker(url, emotion, description="", style="auto"):
    """Download sticker from URL and cache locally."""
    try:
        ext = url.rsplit(".", 1)[-1].split("?")[0] or "png"
        if len(ext) > 5 or ext not in ("png", "jpg", "jpeg", "gif", "webp", "bmp"):
            ext = "png"

        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        style_name = style if style != "auto" else "sticker"
        fname = f"{emotion}_{style_name}_{url_hash}.{ext}"
        file_path = STICKERS_DIR / fname

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
            print(f"⚠️ 下载文件太小 ({len(data)}B)，跳过", file=sys.stderr)
            return None

        file_path.write_bytes(data)
        print(f"📥 已下载: {fname} ({len(data)}B)", file=sys.stderr)

        index = load_json(INDEX_PATH)
        entries = index.get(emotion, [])
        already_exists = False
        for entry in entries:
            if isinstance(entry, dict):
                if entry.get("file") == fname or url_hash in entry.get("file", ""):
                    already_exists = True
                    break
            elif isinstance(entry, str) and entry == fname:
                already_exists = True
                break

        if not already_exists:
            entries.append({
                "file": fname,
                "description": description or f"{emotion}相关表情包",
                "style": style,
            })
            index[emotion] = entries
            save_json(INDEX_PATH, index)

        usage = load_json(USAGE_PATH)
        files = usage.setdefault("files", {})
        files[fname] = {"count": 0, "last_used": "", "tier": "temporary"}
        usage["_last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save_json(USAGE_PATH, usage)

        return {
            "file": fname,
            "path": str(file_path),
            "description": description,
            "style": style,
        }

    except Exception as e:
        print(f"⚠️ 下载失败: {e}", file=sys.stderr)

    return None

def match(text):
    """Main entry: match text to sticker with local-first + web fallback."""
    cleanup_cache()

    emotion = detect_emotion(text)
    if not emotion:
        return {
            "emotion": None, "path": None, "source": "none",
            "description": "", "style": "",
        }

    local_result = search_local(emotion)
    if local_result:
        update_usage(emotion, local_result["file"])
        return {
            "emotion": emotion,
            "path": local_result["path"],
            "source": "local",
            "description": local_result["description"],
            "style": local_result["style"],
        }

    keywords = EMOTIONS.get(emotion, [])
    query = " ".join(keywords[:3]) if keywords else emotion
    style = EMOTION_STYLE.get(emotion, "auto")
    description = EMOTION_DESC.get(emotion, f"{emotion}相关表情包")

    print(f"🔍 联网搜索: [{emotion}] {description} (风格: {style})", file=sys.stderr)
    image_url = search_web(query, style)

    if image_url:
        result = download_sticker(image_url, emotion, description, style)
        if result:
            update_usage(emotion, result["file"])
            return {
                "emotion": emotion,
                "path": result["path"],
                "source": "web",
                "description": result["description"],
                "style": result["style"],
            }

    return {
        "emotion": emotion,
        "path": None,
        "source": "none",
        "description": "",
        "style": "",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python emoji-matcher.py <text>")
        print('Example: python emoji-matcher.py "好开心啊哈哈哈"')
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    result = match(text)

    if result["source"] in ("local", "web"):
        icon = "✅" if result["source"] == "local" else "🌐"
        label = "本地匹配" if result["source"] == "local" else "联网下载"
        print(f"{icon} 匹配成功 [{result['emotion']}] ({label})")
        print(f"📁 {result['path']}")
        if result.get("description"):
            print(f"📝 {result['description']}")
        if result.get("style"):
            print(f"🎨 风格: {result['style']}")
    elif result["source"] == "none" and result["emotion"]:
        print(f"🔍 检测到情绪 [{result['emotion']}]，本地无匹配且搜索无结果")
    else:
        print("💬 未检测到明确情绪")

    print(f"\n{json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
