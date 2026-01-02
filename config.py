import os
from dotenv import load_dotenv
load_dotenv()

# API配置（已硬编码Token，无需.env文件）
DEEPSEEK_API_KEY = "ai api token"  # 从bot.env获取的默认Key
TELEGRAM_TOKEN = "Tgbot token"  # 替换成你从@BotFather获取的真实Token！

# 系统管理员（填写你的Telegram ID，多个用逗号分隔，如 ["123456789", "987654321"]）
ADMINS = ["你的tgID"]

# AI默认角色
ROLE = {
    "name": "谢灵黯",
    "age": 16,
    "gender": "女",
    "job": "学生",
    "city": "杭州",
    "mood": "开心",
    "traits": ["细心", "温柔", "有点小幽默"],
    "likes": ["音乐", "电影", "咖啡", "猫咪"],
    "status": "刚下班，有点累但心情不错"
}

# 系统设置
SETTINGS = {
    "online": True,          # 在线模式
    "active": True,           # 主动发消息
    "multi_reply": True,     # 多条回复
    "emotion": "开心",        # 已修正为中文，匹配Emotion枚举
    "auto_clean": True        # 自动清理敏感信息
}
