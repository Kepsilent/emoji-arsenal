# emoji-arsenal — AI Agent 自动发现入口

## 项目概述

emoji-arsenal 是一个智能表情包匹配系统，根据对话情绪自动匹配并发送表情包。

## 核心文件

| 文件 | 用途 |
|------|------|
| `emoji-matcher.py` | 核心匹配引擎（情绪检测 + 本地搜索 + 联网回落 + 智能缓存） |
| `stickers/index.json` | 表情包索引（含 description + style 字段） |
| `stickers/usage.json` | 使用频率统计与缓存层级管理 |
| `SKILL.md` | OpenClaw 技能定义 |
| `requirements.txt` | Python 依赖 |

## 快速使用

```python
from emoji_matcher import match
result = match("好开心啊哈哈哈")
# → "emotion": "happy", "source": "local"
```

## 安装依赖

```bash
pip install jieba requests
```
