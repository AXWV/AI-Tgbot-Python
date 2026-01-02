import hashlib
import time

class AuthSystem:
    def __init__(self, admins):
        self.admins = set(admins)
        self.sessions = {}
        self.command_history = []
        
    def is_admin(self, user_id):
        """检查是否为管理员"""
        return str(user_id) in self.admins
    
    def verify_command(self, message, user_id):
        """验证系统命令权限"""
        # 检查消息是否为系统命令
        if not message.startswith("//"):
            return False
            
        cmd = message[2:].strip().split()
        if not cmd:
            return False
            
        base_cmd = cmd[0].lower()
        
        # 记录命令历史
        self.command_history.append({
            "time": time.time(),
            "user": user_id,
            "cmd": base_cmd,
            "full": message[:50]
        })
        
        # 保持历史记录长度
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
            
        return self.is_admin(user_id)
    
    def get_command_info(self):
        """获取命令历史"""
        return self.command_history[-10:]  # 返回最近10条