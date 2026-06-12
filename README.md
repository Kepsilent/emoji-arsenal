# emoji-arsenal 🎯

> 智能表情包系统 —— 根据对话情绪自动匹配表情包，越用越聪明

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-orange)](SKILL.md)

**一键安装咒语：**

```
强制重装这个项目，删除旧版本后重新安装最新版：https://github.com/Kepsilent/emoji-arsenal
```

</div>

---

## 📦 功能亮点

| 特性 | 说明 |
|------|------|
| 😊 **情绪感知** | 识别 9 种情绪：开心/难过/爱/生气/惊讶/可爱/点赞/再见/爆笑 |
| 🗂️ **本地缓存** | 优先从本地库匹配，毫秒级响应，无网络也 OK |
| 🌐 **联网搜图** | 本地未命中时自动百度搜图 + 下载缓存 |
| 🔄 **多样性轮换** | 多个表情包时轮流发，不重复不枯燥 |
| ⭐ **智能升温** | 常用表情自动升级为 hot 层级，长期保留 |
| 🗑️ **自动清理** | 低频表情 30 天自动清，热门 60 天无人用也降级 |
| 🎨 **风格匹配** | 搜索时带风格标签（可爱/搞笑/萌），找得更准 |

## 🏗️ 架构

```
用户消息 "好开心啊哈哈哈"
  → detect_emotion() → "happy"
    → search_local() → 命中? → 发图 ✅
                    ↓ 未命中
    → search_web("开心 可爱 表情包")
      → download_sticker() → 缓存 + 发图 🌐
```

**用越多，本地库越丰富，最终几乎不需要联网。**

## 🚀 安装

```bash
# 1. 克隆
git clone https://github.com/Kepsilent/emoji-arsenal.git
cd emoji-arsenal

# 2. 安装依赖
pip install jieba requests

# 3. 试试
python emoji-matcher.py "笑死我了哈哈哈"
```

## 💡 使用方式

**命令行：**
```bash
python emoji-matcher.py "好生气啊烦死了"
# → 🌐 匹配成功 [angry] (联网下载)
# → 📁 stickers/angry_cute_a1b2c3d4.png
# → 📝 生气愤怒的表情包，暴躁抓狂
# → 🎨 风格: angry_style

python emoji-matcher.py "晚安拜拜"
# → ✅ 匹配成功 [goodbye] (本地匹配)
```

**Python API：**
```python
from emoji_matcher import match

result = match("好开心啊哈哈哈")
# {
#   "emotion": "happy",
#   "path": "stickers/开心_咧嘴笑.png",
#   "source": "local",
#   "description": "开心快乐的表情包，笑容灿烂",
#   "style": "cute"
# }
```

**OpenClaw 集成：**
```yaml
# 在 SKILL.md 中配置后，OpenClaw 自动调用
# 用户发消息 → AI 检测情绪 → 自动发图
```

## 🧠 情绪映射

| 情绪 | 英文 | 触发关键词 |
|------|------|-----------|
| 😊 开心 | happy | 开心、哈哈、高兴、兴奋、嘻嘻 |
| 😢 难过 | sad | 难过、哭泣、伤心、呜呜、emo |
| ❤️ 爱 | love | 爱你、亲亲、比心、喜欢、么么哒 |
| 😠 生气 | angry | 生气、愤怒、烦死了、无语 |
| 😲 惊讶 | surprise | 震惊、卧槽、天哪、不会吧 |
| 😳 可爱 | cute | 可爱、卖萌、害羞 |
| 👍 赞同 | approve | 点赞、棒、牛、厉害、666 |
| 👋 再见 | goodbye | 拜拜、晚安、再见、溜了 |
| 🤣 爆笑 | laugh | 笑死、笑cry、🤣、😂、哈哈哈哈 |

## 🔧 缓存策略

```
使用 1-2 次 ──→ temporary（临时，30天清理）
使用 ≥3 次 ──→ hot（热区，60天降级）
初始内置  ──→ bundle（永不清理）
```

## 🛡️ 安全

- 全本地运行，不传输对话内容到第三方
- 联网搜索仅用于下载公开图片
- 无 API Key 需求
- MIT 协议开源

---

<p align="center">Made with ❤️ for <a href="https://github.com/Kepsilent">Kepsilent</a></p>
