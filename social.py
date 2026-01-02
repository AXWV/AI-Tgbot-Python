import json
import networkx as nx
from datetime import datetime

class SocialNetwork:
    def __init__(self):
        self.graph = nx.Graph()
        self.graph.add_node("AI")
        self.relationships = {}
        
    def add_relationship(self, user_id, rel_type):
        """添加关系"""
        uid = str(user_id)
        self.graph.add_node(uid)
        self.graph.add_edge("AI", uid, relationship=rel_type)
        self.relationships[uid] = rel_type
        
        # 唯一关系检查
        unique_rels = ["best_friend", "love", "family"]
        if rel_type in unique_rels:
            # 检查是否已有该关系
            for node, data in self.graph.nodes(data=True):
                if node != "AI" and self.graph.has_edge("AI", node):
                    edge_data = self.graph.get_edge_data("AI", node)
                    if edge_data.get("relationship") == rel_type and node != uid:
                        # 移除旧的关系
                        self.graph.remove_edge("AI", node)
    
    def get_network_info(self):
        """获取网络信息"""
        return {
            "total_users": len(self.graph.nodes()) - 1,
            "relationships": dict(self.relationships),
            "connections": list(self.graph.edges(data=True))
        }
    
    def find_similar_users(self, user_id):
        """寻找相似用户"""
        uid = str(user_id)
        if uid not in self.relationships:
            return []
        
        similar = []
        for node in self.graph.nodes():
            if node != "AI" and node != uid:
                if self.relationships.get(node) == self.relationships[uid]:
                    similar.append(node)
        
        return similar[:3]