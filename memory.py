import json
import os
from datetime import datetime
from collections import defaultdict

class MemorySystem:
    def __init__(self, user_file="users.json"):
        self.user_file = user_file
        self.users = self._load_users()
        self.conversations = defaultdict(list)
        
    def _load_users(self):
        """加载用户数据"""
        if os.path.exists(self.user_file):
            try:
                with open(self.user_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        """保存用户数据"""
        with open(self.user_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def get_user(self, user_id):
        """获取用户信息"""
        uid = str(user_id)
        if uid not in self.users:
            self.users[uid] = {
                "first_seen": datetime.now().isoformat(),
                "message_count": 0,
                "last_active": datetime.now().isoformat(),
                "relationship": "stranger",
                "topics": [],
                "secrets": []
            }
        return self.users[uid]
    
    def add_message(self, user_id, user_msg, ai_msg):
        """添加对话记录"""
        uid = str(user_id)
        user = self.get_user(uid)
        
        # 更新用户数据
        user["message_count"] += 1
        user["last_active"] = datetime.now().isoformat()
        
        # 添加到对话历史
        self.conversations[uid].append({
            "time": datetime.now().isoformat(),
            "user": user_msg[:200],
            "ai": ai_msg[:200]
        })
        
        # 保持最近50条对话
        if len(self.conversations[uid]) > 50:
            self.conversations[uid] = self.conversations[uid][-50:]
        
        # 保存
        self.save_users()
    
    def get_context(self, user_id, limit=5):
        """获取对话上下文"""
        uid = str(user_id)
        if uid in self.conversations:
            return self.conversations[uid][-limit:]
        return []
    
    def update_relationship(self, user_id, relationship):
        """更新关系"""
        uid = str(user_id)
        user = self.get_user(uid)
        user["relationship"] = relationship
        self.save_users()
    
    def add_secret(self, user_id, secret):
        """添加秘密"""
        uid = str(user_id)
        user = self.get_user(uid)
        user["secrets"].append({
            "time": datetime.now().isoformat(),
            "content": secret[:100]
        })
        self.save_users()