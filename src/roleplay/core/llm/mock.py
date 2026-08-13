"""Mock LLM Provider —— 离线可用、确定性回复，用于演示与测试。"""
from .base import LLMPort


class MockLLMProvider(LLMPort):
    def __init__(self, model: str = "mock-model") -> None:
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self,
        *,
        system: str,
        user: str,
        history: list[dict] | None = None,
        temperature: float | None = None,
    ) -> str:
        # 不调用任何外部服务：回显用户原文 + 角色扮演提示，便于断言与演示。
        # 记忆模式下把最近几轮历史拼进回复，直观体现「记得聊过什么」。
        tail = ""
        if history:
            recent = history[-6:]
            tail = "｜稍早的对话：" + "；".join(
                f"{h.get('role')}：「{h.get('content', '')}」" for h in recent
            )
        return (
            f"（角色扮演中）你刚才说：「{user}」{tail}。"
            f"我会以设定好的身份温柔地回应你。"
        )

    async def generate_stream(
        self,
        *,
        system: str,
        user: str,
        history: list[dict] | None = None,
        temperature: float | None = None,
    ):
        # 离线逐片段产出，便于演示打字机/流式效果（约 12 片）。
        text = await self.generate(
            system=system, user=user, history=history, temperature=temperature
        )
        if not text:
            return
        step = max(1, len(text) // 12)
        for i in range(0, len(text), step):
            yield text[i : i + step]
