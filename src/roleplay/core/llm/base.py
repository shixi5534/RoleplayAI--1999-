"""LLM 抽象端口（依赖倒置的契约）。

业务层（Orchestrator）只依赖此接口，不依赖任何具体 SDK / HTTP 客户端。
新增任意 provider = 新增一个实现类，业务层零改动（开闭原则）。
"""
from abc import ABC, abstractmethod


class LLMPort(ABC):
    @abstractmethod
    async def generate(
        self,
        *,
        system: str,
        user: str,
        history: list[dict] | None = None,
        temperature: float | None = None,
    ) -> str:
        """生成回复。实现方负责把 system/history/user 拼成对应协议并调用模型。

        history: OpenAI 格式的过往轮次（不含当前 user），用于「对话记忆」。
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """当前 provider 使用的模型名（用于日志/展示）。"""

    async def generate_stream(
        self,
        *,
        system: str,
        user: str,
        history: list[dict] | None = None,
        temperature: float | None = None,
    ):
        """流式生成（逐 token 产出）。

        默认实现：整段生成后作为单个分片 yield，等价于非流式。
        支持真逐 token 的 provider（如 OpenAI 兼容接口）应覆写此方法，
        在异步生成器中逐块 yield 文本片段。
        """
        text = await self.generate(
            system=system, user=user, history=history, temperature=temperature
        )
        if text:
            yield text
