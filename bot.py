import asyncio
import random
import logging
import aiohttp
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

# ========== 核心配置 ==========
TELEGRAM_TOKEN = "tg bot token"
ADMINS = ["admin telegram ID"]  # 替换为你的TG用户ID
TARGET_USER_ID = "Your telegram ID"
TARGET_RELATION = "The relationship between bot and you"
KEEP_ALIVE_INTERVAL = 60  # 1分钟保活
TYPING_DELAY = 0.5  # 真人秒回延迟
CONTEXT_LENGTH = 10  # 上下文记忆长度

# 网络配置
AI_API_TIMEOUT = 20
RETRY_TIMES = 3

# AI API 配置
DEEPSEEK_API_KEY = "ai api key"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

RELATION_TYPES = ["love", "friend", "close", "family", "stranger"]
RELATION_CMD_PROMPT = f"用法: /set_relation <用户ID> <关系> | 支持: {','.join(RELATION_TYPES)}"

# ========== 日志配置（后台显示用户+回复） ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("chat.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== 上下文记忆管理 ==========
class MemorySystem:
    def __init__(self):
        self.users = {}
        self.users[TARGET_USER_ID] = {
            "relationship": TARGET_RELATION,
            "chat_history": [],
            "locked": True
        }

    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {
                "relationship": "stranger",
                "chat_history": [],
                "locked": False
            }
        return self.users[user_id]

    def update_relationship(self, user_id, rel_type):
        user_data = self.get_user(user_id)
        if user_data["locked"] or rel_type not in RELATION_TYPES:
            return False
        user_data["relationship"] = rel_type
        return True

    def add_chat_history(self, user_id, role, content):
        user_data = self.get_user(user_id)
        user_data["chat_history"].append({"role": role, "content": content})
        if len(user_data["chat_history"]) > CONTEXT_LENGTH:
            user_data["chat_history"] = user_data["chat_history"][-CONTEXT_LENGTH:]

    def get_context(self, user_id):
        user_data = self.get_user(user_id)
        return user_data["chat_history"].copy()

# ========== AI 核心调用（专注主回复+上下文连贯） ==========
async def call_ai_api(user_msg, user_relation, context):
    role_prompts = {
        "love": """你和对象线上聊天，语气亲昵撒娇，像真人唠嗑一样自然。
        一定要参考之前的聊天历史，记住对方说过的话，回复要接得上上一句的话题。
        回复很短，一两句就够，绝对不要括号动作（比如笑、抱抱），内容不重复。""",
        "friend": """你和好朋友线上聊天，语气随意接地气，会接梗吐槽带口头禅。
        参考之前的聊天内容，别跑偏，回复简短自然，不啰嗦。""",
        "stranger": """你和刚认识的人线上聊天，礼貌温和不尴尬，会找小话题但不查户口。
        记住对方说过的基本信息，回复简短，慢慢拉近距离。"""
    }
    system_prompt = role_prompts.get(user_relation, role_prompts["stranger"])

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(context)
    messages.append({"role": "user", "content": user_msg})

    for retry in range(RETRY_TIMES):
        try:
            session = await get_aiohttp_session()
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": DEEPSEEK_MODEL,
                "messages": messages,
                "temperature": 1.0,  # 真人化随机性
                "max_tokens": 100,
                "stream": False
            }
            async with session.post(DEEPSEEK_API_URL, headers=headers, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result["choices"][0]["message"]["content"].strip()
                elif resp.status == 402:
                    return random.choice(["哎呀我这边有点小问题～", "稍等一下下～"])
                else:
                    continue
        except Exception:
            if retry < RETRY_TIMES - 1:
                await asyncio.sleep(0.8)
            else:
                return random.choice(["网络有点卡～", "没听清呢，再说一遍好不好～"])

# ========== 异步会话管理 ==========
async def get_aiohttp_session():
    if not hasattr(get_aiohttp_session, "session"):
        timeout = aiohttp.ClientTimeout(total=AI_API_TIMEOUT)
        get_aiohttp_session.session = aiohttp.ClientSession(timeout=timeout)
    return get_aiohttp_session.session

async def close_aiohttp_session():
    if hasattr(get_aiohttp_session, "session"):
        await get_aiohttp_session.session.close()

# ========== 消息处理器（移除追加回复，专注一对一聊天） ==========
class BotHandlers:
    def __init__(self):
        self.memory = MemorySystem()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def handle_message(self, update: Update, context: CallbackContext):
        user_id = str(update.effective_user.id)
        user_name = update.effective_user.username or "未知用户"
        user_msg = update.message.text.strip()
        user_data = self.memory.get_user(user_id)
        user_relation = user_data["relationship"]
        chat_context = self.memory.get_context(user_id)

        # 记录用户消息到上下文
        self.memory.add_chat_history(user_id, "user", user_msg)
        logger.info(f"用户[{user_id}({user_name})] | 发送: {user_msg}")

        # 模拟真人打字
        update.message.chat.send_action(action="typing")
        self.loop.run_until_complete(asyncio.sleep(TYPING_DELAY))

        # 生成主回复（无追加）
        main_resp = self.loop.run_until_complete(call_ai_api(user_msg, user_relation, chat_context))
        update.message.reply_text(main_resp)
        
        # 记录Bot回复到上下文
        self.memory.add_chat_history(user_id, "assistant", main_resp)
        logger.info(f"用户[{user_id}({user_name})] | Bot回复: {main_resp}")

    def handle_status(self, update: Update, context: CallbackContext):
        user_id = str(update.effective_user.id)
        if user_id not in ADMINS:
            update.message.reply_text("你没有权限哦～")
            return
        active_users = len(self.memory.users)
        resp = f"""🤖 聊天Bot状态
├─ 活跃用户数: {active_users}
├─ 保活间隔: {KEEP_ALIVE_INTERVAL}秒
├─ 上下文记忆长度: {CONTEXT_LENGTH}条
└─ 锁定情侣用户: {TARGET_USER_ID}"""
        update.message.reply_text(resp)
        logger.info(f"管理员[{user_id}] | 查看状态")

    def handle_set_relation(self, update: Update, context: CallbackContext):
        user_id = str(update.effective_user.id)
        if user_id not in ADMINS:
            update.message.reply_text("你没有权限哦～")
            return
        if len(context.args) != 2:
            update.message.reply_text(RELATION_CMD_PROMPT)
            return
        target_uid, rel_type = context.args[0], context.args[1]
        if self.memory.update_relationship(target_uid, rel_type):
            update.message.reply_text(f"✅ 已将用户[{target_uid}]设为{rel_type}关系")
        else:
            update.message.reply_text(f"❌ 设置失败（用户锁定或关系无效）")

    def error_handler(self, update: Update, context: CallbackContext):
        logger.error(f"系统错误: {str(context.error)}")
        if update:
            update.message.reply_text("哎呀，出了点小问题～")

# ========== 聊天记录导出功能 ==========
def export_chat_history(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in ADMINS:
        update.message.reply_text("你没有权限导出聊天记录哦～")
        return
    if len(context.args) != 1:
        update.message.reply_text("用法: /export <目标用户ID>")
        return
    target_uid = context.args[0]
    memory = BotHandlers().memory
    if target_uid not in memory.users:
        update.message.reply_text(f"用户[{target_uid}]不存在～")
        return
    chat_history = memory.get_context(target_uid)
    if not chat_history:
        update.message.reply_text(f"用户[{target_uid}]暂无聊天记录～")
        return
    export_content = f"=== 用户[{target_uid}]聊天记录 ===\n"
    for msg in chat_history:
        role = "用户" if msg["role"] == "user" else "Bot"
        export_content += f"{role}: {msg['content']}\n"
    export_content += "=== 导出结束 ==="
    with open(f"chat_export_{target_uid}.txt", "w", encoding="utf-8") as f:
        f.write(export_content)
    update.message.reply_text(f"✅ 聊天记录已导出到: chat_export_{target_uid}.txt")
    logger.info(f"管理员[{user_id}] | 导出用户[{target_uid}]聊天记录")

# ========== 启动Bot ==========
def main():
    handlers = BotHandlers()
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("status", handlers.handle_status))
    dp.add_handler(CommandHandler("set_relation", handlers.handle_set_relation))
    dp.add_handler(CommandHandler("export", export_chat_history))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handlers.handle_message))
    dp.add_error_handler(handlers.error_handler)

    # 1分钟保活任务
    def keep_alive():
        logger.info("保活任务 | Bot正常运行中")
        handlers.loop.call_later(KEEP_ALIVE_INTERVAL, keep_alive)
    keep_alive()

    print("\n💬 真人感聊天Bot启动成功！")
    print("✅ 特性：上下文记忆 | 后台日志 | 1分钟保活 | 无重复追加回复")
    print("🔧 管理员命令：/status | /set_relation <ID> <关系> | /export <用户ID>")

    updater.start_polling(timeout=30, read_latency=2)
    updater.idle()

    # 关闭资源
    handlers.loop.run_until_complete(close_aiohttp_session())
    handlers.loop.close()

if __name__ == "__main__":
    main()
