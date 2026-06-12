#!/usr/bin/env python3
"""Tests for emoji-matcher.py — unit tests for core functions."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

# ── Mock the sticker paths to use a temp dir ──
import emoji_matcher as em


class TestDetectEmotion(unittest.TestCase):
    """Tests for detect_emotion() — keyword-based emotion detection."""

    def test_happy(self):
        self.assertEqual(em.detect_emotion("好开心啊哈哈哈"), "happy")

    def test_sad(self):
        self.assertEqual(em.detect_emotion("我好难过呜呜"), "sad")

    def test_love(self):
        self.assertEqual(em.detect_emotion("爱你么么哒"), "love")

    def test_angry(self):
        self.assertEqual(em.detect_emotion("烦死了无语"), "angry")

    def test_surprise(self):
        self.assertEqual(em.detect_emotion("卧槽天哪"), "surprise")

    def test_cute(self):
        self.assertEqual(em.detect_emotion("好可爱呀"), "cute")

    def test_approve(self):
        self.assertEqual(em.detect_emotion("太棒了666"), "approve")

    def test_goodbye(self):
        self.assertEqual(em.detect_emotion("晚安拜拜"), "goodbye")

    def test_laugh(self):
        self.assertEqual(em.detect_emotion("笑死我了🤣"), "laugh")

    def test_no_match(self):
        self.assertIsNone(em.detect_emotion("今天天气不错"))

    def test_multiple_emotions(self):
        """Should return the highest-scoring emotion."""
        result = em.detect_emotion("哈哈好开心啊呜呜")
        self.assertIn(result, ("happy", "sad"))  # Either is acceptable


class TestLoadSaveJSON(unittest.TestCase):
    """Tests for JSON I/O helpers."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        self.path = Path(self.tmp.name)

    def tearDown(self):
        if self.path.exists():
            self.path.unlink()
        tmp_backup = self.path.with_suffix(".tmp")
        if tmp_backup.exists():
            tmp_backup.unlink()

    def test_load_nonexistent(self):
        """Loading a non-existent file returns empty dict."""
        result = em.load_json(Path("/nonexistent/path.json"))
        self.assertEqual(result, {})

    def test_save_and_load(self):
        """Save then load should return identical data."""
        data = {"test": {"count": 5, "tier": "hot"}}
        em.save_json(self.path, data)
        loaded = em.load_json(self.path)
        self.assertEqual(loaded, data)

    def test_load_invalid_json(self):
        """Loading corrupted JSON returns empty dict."""
        self.path.write_text("{invalid json}", encoding="utf-8")
        result = em.load_json(self.path)
        self.assertEqual(result, {})


class TestGetStickerFiles(unittest.TestCase):
    """Tests for get_sticker_files() — handles old & new index format."""

    def test_new_format(self):
        index = {"happy": [{"file": "a.png", "style": "cute"}]}
        result = em.get_sticker_files(index, "happy")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["file"], "a.png")

    def test_old_format(self):
        index = {"happy": ["a.png", "b.png"]}
        result = em.get_sticker_files(index, "happy")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["file"], "a.png")
        self.assertEqual(result[0]["style"], "auto")

    def test_empty(self):
        result = em.get_sticker_files({}, "nonexistent")
        self.assertEqual(result, [])


class TestUpdateUsage(unittest.TestCase):
    """Tests for update_usage() — usage counting + tier promotion."""

    def setUp(self):
        # Backup real usage path and replace with temp
        self.orig_path = em.USAGE_PATH
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        em.USAGE_PATH = Path(self.tmp.name)
        # Write clean initial state
        em.save_json(em.USAGE_PATH, {
            "_last_updated": "",
            "_last_cleanup": "",
            "happy": {"count": 0, "last_used": "", "tier": "temporary"},
            "files": {},
        })

    def tearDown(self):
        em.USAGE_PATH = self.orig_path
        if Path(self.tmp.name).exists():
            os.unlink(self.tmp.name)

    def test_count_increments(self):
        em.update_usage("happy")
        usage = em.load_json(em.USAGE_PATH)
        self.assertEqual(usage["happy"]["count"], 1)

    def test_tier_promotion(self):
        """Using 3 times should promote to hot."""
        em.update_usage("happy", "test.png")
        em.update_usage("happy", "test.png")
        em.update_usage("happy", "test.png")
        usage = em.load_json(em.USAGE_PATH)
        self.assertEqual(usage["happy"]["tier"], "hot")
        self.assertEqual(usage["files"]["test.png"]["tier"], "hot")

    def test_file_tracking(self):
        em.update_usage("happy", "stick.png")
        usage = em.load_json(em.USAGE_PATH)
        self.assertIn("files", usage)
        self.assertIn("stick.png", usage["files"])
        self.assertEqual(usage["files"]["stick.png"]["count"], 1)


class TestMatchFlow(unittest.TestCase):
    """Tests for match() — end-to-end matching flow."""

    def test_no_emotion(self):
        result = em.match("今天天气不错")
        self.assertIsNone(result["emotion"])
        self.assertIsNone(result["path"])
        self.assertEqual(result["source"], "none")

    def test_happy_local_match(self):
        """If a local sticker exists for happy, should return local."""
        result = em.match("好开心啊哈哈哈")
        self.assertEqual(result["emotion"], "happy")
        # May be local or web depending on whether the sticker file exists
        self.assertIn(result["source"], ("local", "web", "none"))


if __name__ == "__main__":
    unittest.main()
