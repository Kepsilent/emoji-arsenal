# emoji-arsenal 安装指南

## 一键安装

复制以下咒语给你的 AI Agent：

```
强制重装这个项目，删除旧版本后重新安装最新版：https://github.com/Kepsilent/emoji-arsenal
```

## 手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/Kepsilent/emoji-arsenal.git
cd emoji-arsenal

# 2. 安装 Python 依赖
pip install jieba requests

# 3. 运行测试
python emoji-matcher.py "好开心啊哈哈哈"
```

## 验证安装

```bash
# 应该输出：
# ✅ 匹配成功 [happy] (本地匹配)
# 📁 ...stickers/开心_咧嘴笑.png
python emoji-matcher.py "好开心啊哈哈哈"
```

## OpenClaw 集成

在 OpenClaw Gateway 中启用 `emoji-arsenal` Skill 即可自动集成。
