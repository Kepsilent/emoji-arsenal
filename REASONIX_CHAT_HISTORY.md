# emoji-arsenal Skill — 开发对话记录

> 与 Reasonix AI Agent 协作完成，2026-06-11 ~ 2026-06-12

---

## 项目背景

用户在部署完本地 llama.cpp 模型后，希望搭建一个智能表情包系统给 OpenClaw 使用。核心理念：根据对话情绪自动匹配表情包发图，而不是让用户手动搜索。

经调研，市面上不存在同类 AI 语义表情包匹配系统，此项目为首创。

---

## 核心设计理念

### 双模式架构

| 模式 | 描述 | 触发条件 |
|------|------|---------|
| **方案一：联网搜** | web_search → 下载表情包 → 发送 | 本地库未命中 |
| **方案二：本地缓存** | 查 stickers/index.json → 直接发图 | 本地库已命中 |

**高频使用的方案一结果自动缓存到方案二。** 使用越频繁，本地库越丰富，最终几乎不需要联网搜索。

---

## 技术架构

```
用户消息: "好开心啊哈哈哈哈"
  ↓
emoji-matcher.py: detect_emotion("好开心啊哈哈哈哈")
  → 识别情绪: happy
  ↓
search_local("happy")
  ├─ 命中 → 返回本地文件路径 → OpenClaw 发图 ✅
  └─ 未命中 → web_search("开心 表情包") → 下载 → 发图 + 缓存 ✅
  ↓
update_usage("happy") → usage.json 频率 +1
  └─ 每月清理 30 天内未使用的缓存
```

---

## 情绪关键词映射

| 情绪 | 英文 | 关键词 |
|------|------|--------|
| 开心 | happy | 开心、哈哈、高兴、快乐、兴奋、嘻嘻 |
| 难过 | sad | 难过、哭泣、伤心、呜呜、emo |
| 爱 | love | 爱你、亲亲、比心、喜欢、么么哒 |
| 生气 | angry | 生气、愤怒、烦死了、无语 |
| 惊讶 | surprise | 震惊、卧槽、天哪、不会吧 |
| 可爱 | cute | 可爱、卖萌、害羞 |
| 赞同 | approve | 点赞、棒、牛、厉害、666 |
| 再见 | goodbye | 拜拜、晚安、再见、溜了 |
| 爆笑 | laugh | 笑死、笑cry、🤣、😂、哈哈哈哈 |

---

## 目录结构

```
emoji-arsenal/
├── SKILL.md              # OpenClaw 技能定义
├── README.md             # 开源文档
├── LICENSE               # MIT 协议
├── emoji-matcher.py      # 核心匹配引擎
├── requirements.txt      # Python 依赖（jieba）
├── stickers/             # 本地表情包库
│   ├── index.json        # 关键词 → 文件映射
│   ├── usage.json        # 使用频率统计
│   ├── 开心_咧嘴笑.png
│   ├── 哭泣_大哭.png
│   ├── 爱心_红心.png
│   ├── 点赞_赞.png
│   ├── 笑哭_笑cry.png
│   └── 害羞_花痴.png
└── scripts/
    └── download_sticker.py  # URL 下载工具
```

---

## 对比 vision-analyzer

| 特性 | vision-analyzer | emoji-arsenal |
|------|:--:|:--:|
| 方向 | 图 → 文字（识图） | 文字 → 图（发图） |
| 触发 | 用户发图片 | 对话情绪关键词 |
| 模型调用 | llama-server vision API | 无需模型 |
| 联网 | 不需要 | 可选（未命中时） |
| 适用 | Reasonix | OpenClaw |

---

## 安全设计

- 全本地运行，不传输对话内容到第三方
- 联网搜索仅用于下载公开图片
- 不读取用户目录以外的文件
- 无 API Key 需求
- MIT 协议开源

---

## GitHub 信息

- 账号：Kepsilent
- 仓库：emoji-arsenal（待推送）
- 协议：MIT

---

*此项目由用户与 Reasonix AI Agent 协作完成。*
