import json
import os
import random
import re
from datetime import datetime
from enum import Enum

class Emotion(Enum):
    HAPPY = "开心"
    SAD = "伤心"
    ANGRY = "生气"
    EXCITED = "兴奋"
    CALM = "平静"
    ROMANTIC = "浪漫"
    LONELY = "孤独"
    NERVOUS = "紧张"

class AICore:
    def __init__(self, role_config, settings):
        self.role = role_config
        self.settings = settings.copy()
        self.state_file = "state.json"
        self.load_state()
        
        # 情感系统
        self.emotion = Emotion(self.settings["emotion"])
        self.energy = 80  # 能量值 0-100
        self.mood_history = []
        
        # 个性系统
        self.personality = {
            "openness": 0.7,
            "extraversion": 0.6,
            "agreeableness": 0.8,
            "neuroticism": 0.3,
            "conscientiousness": 0.7
        }
        
        # 实时状态
        self.current_context = ""
        
    def load_state(self):
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings.update(data.get("settings", {}))
                    self.role.update(data.get("role", {}))
            except:
                pass
    
    def save_state(self):
        """保存状态"""
        data = {
            "role": self.role,
            "settings": self.settings,
            "last_update": datetime.now().isoformat()
        }
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def process_command(self, command):
        """处理系统命令"""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False, "无效命令"
        
        base_cmd = cmd_parts[0].lower()
        
        try:
            if base_cmd == "info":
                return self._get_info()
            elif base_cmd == "role":
                return self._update_role(cmd_parts[1:])
            elif base_cmd == "online":
                return self._set_online(cmd_parts[1:])
            elif base_cmd == "emotion":
                return self._set_emotion(cmd_parts[1:])
            elif base_cmd == "active":
                return self._set_active(cmd_parts[1:])
            elif base_cmd == "multi":
                return self._set_multi(cmd_parts[1:])
            elif base_cmd == "relation":
                return self._set_relation(cmd_parts[1:])
            elif base_cmd == "personality":
                return self._set_personality(cmd_parts[1:])
            elif base_cmd == "traits":
                return self._set_traits(cmd_parts[1:])
            elif base_cmd == "clean":
                return self._clean_data()
            else:
                return False, f"未知命令: {base_cmd}"
        except Exception as e:
            return False, f"命令错误: {str(e)}"
    
    def _get_info(self):
        """获取系统信息"""
        info = [
            f"🤖 AI状态报告",
            f"━━━━━━━━━━━━━━",
            f"角色: {self.role['name']} ({self.role['age']}岁)",
            f"心情: {self.emotion.value} (能量: {self.energy}%)",
            f"模式: {'在线' if self.settings['online'] else '离线'}",
            f"主动: {'开启' if self.settings['active'] else '关闭'}",
            f"多回复: {'开启' if self.settings['multi_reply'] else '关闭'}",
            f"━━━━━━━━━━━━━━",
            f"设置: 使用 //命令 参数 来修改"
        ]
        return True, "\n".join(info)
    
    def _update_role(self, args):
        """更新角色信息"""
        if len(args) < 2:
            return False, "格式: role 字段=值"
        
        updates = {}
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                if key in self.role:
                    if key == "age":
                        value = int(value)
                    elif key == "traits":
                        value = value.split(',')
                    elif key == "likes":
                        value = value.split(',')
                    
                    self.role[key] = value
                    updates[key] = value
        
        self.save_state()
        return True, f"角色更新: {updates}"
    
    def _set_online(self, args):
        """设置在线模式"""
        if not args:
            return False, "格式: online on/off"
        
        mode = args[0].lower()
        if mode == "on":
            self.settings["online"] = True
            msg = "在线模式已开启"
        elif mode == "off":
            self.settings["online"] = False
            msg = "离线模式已开启"
        else:
            return False, "参数错误: on 或 off"
        
        self.save_state()
        return True, msg
    
    def _set_emotion(self, args):
        """设置情感"""
        if not args:
            return False, "格式: emotion 情感"
        
        emotion_str = args[0].lower()
        emotion_map = {
            "happy": "开心", "sad": "伤心", "angry": "生气",
            "excited": "兴奋", "calm": "平静", "romantic": "浪漫",
            "lonely": "孤独", "nervous": "紧张"
        }
        
        if emotion_str in emotion_map:
            self.emotion = Emotion(emotion_map[emotion_str])
            self.settings["emotion"] = emotion_str
            self.save_state()
            return True, f"情感已设为: {self.emotion.value}"
        else:
            return False, f"未知情感，可用: {', '.join(emotion_map.keys())}"
    
    def _set_active(self, args):
        """设置主动模式"""
        if not args:
            return False, "格式: active on/off"
        
        mode = args[0].lower()
        self.settings["active"] = (mode == "on")
        self.save_state()
        status = "开启" if self.settings["active"] else "关闭"
        return True, f"主动消息已{status}"
    
    def _set_multi(self, args):
        """设置多条回复"""
        if not args:
            return False, "格式: multi on/off"
        
        mode = args[0].lower()
        self.settings["multi_reply"] = (mode == "on")
        self.save_state()
        status = "开启" if self.settings["multi_reply"] else "关闭"
        return True, f"多条回复已{status}"
    
    def _set_relation(self, args):
        """设置关系"""
        if not args:
            return False, "格式: relation 关系类型"
        
        rel_type = args[0].lower()
        valid_types = ["stranger", "friend", "close", "love", "family", "best"]
        
        if rel_type not in valid_types:
            return False, f"无效关系，可用: {', '.join(valid_types)}"
        
        self.save_state()
        return True, f"关系已设为: {rel_type}"
    
    def _set_personality(self, args):
        """设置性格"""
        if len(args) < 2:
            return False, "格式: personality 特质 值(0-1)"
        
        trait = args[0].lower()
        try:
            value = float(args[1])
            value = max(0, min(1, value))
            
            if trait in self.personality:
                self.personality[trait] = value
                return True, f"{trait} 已设为 {value:.2f}"
            else:
                return False, f"未知特质: {trait}"
        except ValueError:
            return False, "值必须是数字"
    
    def _set_traits(self, args):
        """设置个性"""
        if not args:
            return False, "格式: traits 特质1,特质2,..."
        
        traits = args[0].split(',')
        self.role["traits"] = traits
        self.save_state()
        return True, f"个性已更新: {', '.join(traits)}"
    
    def _clean_data(self):
        """清理数据"""
        import shutil
        import glob
        
        # 清理临时文件
        for file in glob.glob("temp_*"):
            try:
                os.remove(file)
            except:
                pass
        
        return True, "数据已清理"
    
    def get_response_template(self):
        """根据当前状态获取回复模板"""
        templates = {
            "happy": [
                "今天心情真不错！",
                "hhh 好开心呀~",
                "感觉今天会有好事发生！😊"
            ],
            "sad": [
                "唉...有点难过",
                "心情不太好...",
                "让我一个人静静 😔"
            ],
            "romantic": [
                "❤️ 今天特别想你",
                "心里暖暖的~",
                "和你聊天总是很开心 🥰"
            ],
            "calm": [
                "嗯...我在听",
                "感觉挺平静的",
                "今天过得还不错"
            ]
        }
        
        # 根据情感选择模板
        emotion_key = self.settings["emotion"]
        if emotion_key in templates:
            return random.choice(templates[emotion_key])
        
        # 默认模板
        return random.choice(["嗯...", "我在听呢", "然后呢？"])
    
    def update_energy(self, user_message):
        """更新能量值"""
        # 根据消息内容调整能量
        positive = len(re.findall(r'[好开心快乐棒棒棒]', user_message))
        negative = len(re.findall(r'[难过伤心生气烦累]', user_message))
        
        self.energy += positive * 2
        self.energy -= negative * 3
        self.energy = max(0, min(100, self.energy))
        
        # 记录心情
        self.mood_history.append({
            "time": datetime.now().isoformat(),
            "energy": self.energy,
            "emotion": self.emotion.value
        })
        
        if len(self.mood_history) > 100:
            self.mood_history = self.mood_history[-100:]