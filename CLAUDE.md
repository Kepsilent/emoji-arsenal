# emoji-arsenal — Claude Code 路由

## 项目类型
Python CLI 工具 / OpenClaw Skill

## 关键文件
- `emoji-matcher.py` — 主程序，一切从此开始
- `stickers/index.json` — 表情包索引
- `stickers/usage.json` — 使用统计与缓存管理

## 常用命令
```bash
# 测试情绪匹配
python emoji-matcher.py "好开心啊哈哈哈"

# 测试联网搜索
python emoji-matcher.py "好生气啊烦死了"
```

## 架构说明
用户消息 → 情绪检测 → 本地匹配（多样性轮选）→ 未命中则联网搜索 → 自动缓存
