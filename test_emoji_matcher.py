#!/usr/bin/env python3
"""Tests for emoji-matcher.py — unit tests for core functions.

All tests use temp directories and mock network calls.
No real files are modified and no real HTTP requests are made.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.resolve()))
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
        """非情绪文本应返回 None — 不含"气"字避免误判"""
        self.assertIsNone(em.detect_emotion("今天天气不错"))

    def test_weather_not_angry(self):
        """含"天气"不应触发 angry（"气"已移除）"""
        result = em.detect_emotion("今天的天气真不错啊")
        self.assertIsNone(result)

    def test_happy_wins_over_sad(self):
        """两个情绪都匹配时，返回得分最高的"""
        result = em.detect_emotion("哈哈好开心啊呜呜")
        # "开心"(2) + "哈哈"(2) = 4 for happy; "呜呜"(2) = 2 for sad
        self.assertEqual(result, "happy")


class TestLoadSaveJSON(unittest.TestCase):
    """Tests for JSON I/O helpers."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        self.path = Path(self.tmp.name)
        self.tmp.close()

    def tearDown(self):
        if self.path.exists():
            self.path.unlink()
        tmp_backup = self.path.with_suffix(".tmp")
        if tmp_backup.exists():
            tmp_backup.unlink()

    def test_load_nonexistent(self):
        result = em.load_json(Path("/nonexistent/path.json"))
        self.assertEqual(result, {})

    def test_save_and_load(self):
        data = {"test": {"count": 5, "tier": "hot"}}
        em.save_json(self.path, data)
        loaded = em.load_json(self.path)
        self.assertEqual(loaded, data)

    def test_load_invalid_json(self):
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
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        self.usage_file = self.tmp_path / "usage.json"
        self.index_file = self.tmp_path / "index.json"

        # Init test files
        em.save_json(self.usage_file, {
            "_last_updated": "",
            "_last_cleanup": "",
            "happy": {"count": 0, "last_used": "", "tier": "temporary"},
            "files": {},
        })
        em.save_json(self.index_file, {
            "happy": [{"file": "test.png", "description": "test", "style": "cute"}],
        })

    def tearDown(self):
        self.tmp_dir.cleanup()

    @patch("emoji_matcher.USAGE_PATH")
    @patch("emoji_matcher.INDEX_PATH")
    @patch("emoji_matcher.STICKERS_DIR")
    def test_count_increments(self, mock_stickers, mock_index, mock_usage):
        mock_usage.__fspath__ = lambda: str(self.usage_file)
        mock_index.__fspath__ = lambda: str(self.index_file)
        mock_stickers.__fspath__ = lambda: str(self.tmp_path)

        # Override module attributes
        orig_usage = em.USAGE_PATH
        orig_index = em.INDEX_PATH
        em.USAGE_PATH = self.usage_file
        em.INDEX_PATH = self.index_file

        try:
            em.update_usage("happy")
            usage = em.load_json(self.usage_file)
            self.assertEqual(usage["happy"]["count"], 1)
        finally:
            em.USAGE_PATH = orig_usage
            em.INDEX_PATH = orig_index

    @patch("emoji_matcher.USAGE_PATH")
    @patch("emoji_matcher.INDEX_PATH")
    @patch("emoji_matcher.STICKERS_DIR")
    def test_tier_promotion(self, mock_stickers, mock_index, mock_usage):
        orig_usage = em.USAGE_PATH
        orig_index = em.INDEX_PATH
        em.USAGE_PATH = self.usage_file
        em.INDEX_PATH = self.index_file
        try:
            em.update_usage("happy", "test.png")
            em.update_usage("happy", "test.png")
            em.update_usage("happy", "test.png")
            usage = em.load_json(self.usage_file)
            self.assertEqual(usage["happy"]["tier"], "hot")
            self.assertEqual(usage["files"]["test.png"]["tier"], "hot")
        finally:
            em.USAGE_PATH = orig_usage
            em.INDEX_PATH = orig_index


class TestMatchFlow(unittest.TestCase):
    """Tests for match() — end-to-end with mocked network."""

    def test_no_emotion(self):
        result = em.match("今天天气不错")
        self.assertIsNone(result["emotion"])
        self.assertIsNone(result["path"])
        self.assertEqual(result["source"], "none")

    @patch("emoji_matcher.cleanup_cache", return_value=[])
    @patch("emoji_matcher.search_web", return_value=None)
    def test_happy_local_nofile(self, mock_search, mock_cleanup):
        """Happy emotion detected but no local file, web returns None."""
        # Point to temp index with no files
        with tempfile.TemporaryDirectory() as td:
            tpath = Path(td)
            idx = tpath / "index.json"
            usg = tpath / "usage.json"
            em.save_json(idx, {"happy": [], "sad": []})
            em.save_json(usg, {"files": {}, "_last_updated": "", "_last_cleanup": ""})

            orig_idx, orig_usg, orig_stick = em.INDEX_PATH, em.USAGE_PATH, em.STICKERS_DIR
            em.INDEX_PATH = idx
            em.USAGE_PATH = usg
            em.STICKERS_DIR = tpath

            try:
                result = em.match("好开心啊哈哈哈")
                self.assertEqual(result["emotion"], "happy")
                self.assertEqual(result["source"], "none")
                self.assertIsNone(result["path"])
            finally:
                em.INDEX_PATH = orig_idx
                em.USAGE_PATH = orig_usg
                em.STICKERS_DIR = orig_stick


if __name__ == "__main__":
    unittest.main()
