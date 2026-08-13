"""RoleplayAI —— 角色扮演 AI 整合项目（Clean Architecture）。

包结构：
    roleplay.api        # 接口适配层（FastAPI 路由）
    roleplay.core       # 应用层 + 端口/适配器（llm / emotion / rag）
    roleplay.errors     # 统一异常体系
    roleplay.models     # DTO 与领域模型
"""
__version__ = "0.1.0"
