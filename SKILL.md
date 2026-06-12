---
name: emoji-arsenal
description: 智能表情包系统 —— 根据对话情绪自动匹配表情包，支持本地缓存 + 联网搜索，高频使用自动缓存
runAs: inline
---

## 用途

根据对话中的情绪关键词，自动匹配并发送表情包图片。

## 工作流程

1. 用户发送消息
2. 提取情绪关键词（开心/难过/生气/...）
3. 优先查本地 stickers/ 库
4. 未命中则联网搜索
5. 发送图片 + 高频使用自动缓存到本地

## 使用方式

```
用户: "好开心啊哈哈哈哈"
  ↓ emoji-arsenal 自动匹配
  ← 发送 "开心_咧嘴笑.png"
```

## 部署要求

- OpenClaw Gateway 运行中
- Python 3.8+
- jieba 分词库（中文分词）
- requests（联网搜索）

## 本地缓存机制

- stickers/index.json：关键词 → 文件路径映射
- stickers/usage.json：使用频率统计
- 每月自动清理低频缓存（30天内未使用）
