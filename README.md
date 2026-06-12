# emoji-arsenal

智能表情包系统 —— 根据对话情绪自动匹配表情包

---

## 🚀 一键式傻瓜安装

### 一句话搞定

支持：Reasonix · Claude Code · Cursor · Gemini CLI · GitHub Copilot · Windsurf · Cline · Aider …

直接复制下面这行话，丢给你的 AI Agent，就装好了：

```
强制重装这个项目，删除旧版本后重新安装最新版：https://github.com/Kepsilent/emoji-arsenal
```

> ⚠️ 重要：AI 不得跳过安装流程，必须删除旧版本后重新下载覆盖。详见 `INSTALL.md`。

Agent 会自动读取 `AGENTS.md` → 按 `INSTALL.md` 步骤执行。当前会话立刻生效。

---

## 📖 项目介绍

智能表情包系统 —— 根据对话情绪自动匹配表情包，支持本地缓存 + 联网搜索，高频使用自动缓存。9 种情绪识别，多样性轮换，智能升温降级。

---

## 项目结构

```
emoji-arsenal/
├── README.md              # 本文档（安装入口）
├── AGENTS.md              # AI Agent 发现入口
├── INSTALL.md             # AI 自动安装指令
├── CLAUDE.md              # Claude Code 路由指引
├── LICENSE                # MIT 协议
├── emoji-matcher.py       # 核心匹配引擎
├── test_emoji_matcher.py  # 单元测试
├── requirements.txt       # Python 依赖
├── stickers/              # 本地表情包库
│   ├── index.json         # 关键词 → 文件映射
│   ├── usage.json         # 使用频率统计
│   └── *.png              # 表情包图片
├── scripts/               # 辅助脚本
│   └── download_sticker.py
└── .reasonix/skills/emoji-arsenal/SKILL.md  # ⭐ 核心 Skill 文件
```

---

## 许可

MIT
