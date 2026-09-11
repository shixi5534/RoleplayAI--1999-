"""外部消息渠道包（QQ / OneBot 等）。

每个渠道是一个独立适配器：把外部平台的消息转成内部 ChatRequest，
调用 ChatOrchestrator，再把 ChatResponse 发回平台。大脑复用，互不干扰。
"""
from .qq_onebot import QQChannel, start_qq_channel

__all__ = ["QQChannel", "start_qq_channel"]
