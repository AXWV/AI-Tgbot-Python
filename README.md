# AI-Tgbot-Python
专门为termux而制作的tgbot系统
Termux-Telegram-ChatBot: 轻量智能聊天机器人
 
A lightweight, context-aware Telegram chatbot tailored for Termux environment, featuring natural human-like conversation, user context memory, and admin management tools.
 
✨ Core Features
 
- Natural Chat Experience
Simulates real-person dialogue with role-based tone (lover/friend/stranger), no rigid or repetitive responses.
- Context Memory
Retains the latest 10 rounds of conversation history to ensure coherent topic continuity.
- Admin Management Tools
- View bot status with  /status 
- Modify user chat roles with  /set_relation 
- Export chat history to text files with  /export 
- Termux-Optimized
Low resource consumption, asynchronous request processing, and 1-minute keep-alive mechanism for stable long-term operation.
- Detailed Logging
Records user messages and bot responses in both terminal and log files for easy debugging and monitoring.
 
🚀 Quick Start (Termux Environment)
 
1. Environment Preparation
 
bash
  
# Update Termux packages
pkg update && pkg upgrade -y

# Install Python & pip
pkg install python3 python3-pip -y

# Install dependencies
pip3 install python-telegram-bot==13.7 aiohttp==3.9.1 pytz==2023.3
 
 
2. Configuration
 
1. Get your Telegram Bot Token from @BotFather
2. Get your AI API Key (supports DeepSeek API)
3. Modify the following parameters in the code:
python
  
TELEGRAM_TOKEN = "your-bot-token-here"
DEEPSEEK_API_KEY = "your-ai-api-key-here"
ADMINS = ["your-telegram-user-id"]
 
 
3. Run the Bot
 
bash
  
python3 chatbot.py
 
 
📋 Admin Commands
 
Command Description 
 /status  Check active user count, context length and other bot status 
 /set_relation <user-id> <role>  Set user chat role (love/friend/stranger) 
 /export <user-id>  Export specified user's chat history to a txt file 
 
🛠️ Technical Stack
 
- Language: Python 3.8+
- Telegram API: python-telegram-bot==13.7
- Asynchronous HTTP: aiohttp
- Timezone Handling: pytz
 
📝 Notes
 
1. Ensure Termux has network access and can connect to Telegram and AI API servers
2. The bot uses asynchronous processing to avoid blocking during long requests
3. Chat history is stored locally and will be cleared when the bot restarts (modify the code to enable persistent storage if needed)
 
🤝 Contribution
 
Feel free to submit issues and pull requests for feature enhancements, bug fixes and optimization.
