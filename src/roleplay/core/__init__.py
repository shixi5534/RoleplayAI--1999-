"""应用层与端口/适配器（core）。

分层：
    core.orchestrator   # 应用层用例：一次对话的编排
    core.llm            # LLM 端口 + 适配器
    core.emotion        # 情感检测端口 + 适配器 + Live2D 映射
    core.rag            # 向量库端口 + 适配器
"""
