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
        system_blocks: list[str] | None = None,
        user_prefix: str | None = None,
    ) -> str:
        """生成回复。实现方负责把 system/history/user 拼成对应协议并调用模型。

        history: OpenAI 格式的过往轮次（不含当前 user），用于「对话记忆」。

        P1-1 分层消息（均为**可选**；不传时行为与改造前完全一致，零回归）：
        - system_blocks：非空时**取代** system，按顺序展开为多条 system 消息
          （核心人设 / 用户画像 / RAG 资料各自成条，消息边界便于注意力定位）；
        - user_prefix：非空时拼在当前 user 消息**之前**，承载「怎么说」的动态指令
          （情绪策略 / 情感节奏 / 长度 / 风格 / 核心锚点 / 复读抑制）。

        不支持多 system 消息的端点可安全忽略这两个参数（回退单 system），
        因此本契约只要求"能接受"，不强制"必须实现"。
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
        system_blocks: list[str] | None = None,
        user_prefix: str | None = None,
    ):
        """流式生成（逐 token 产出）。

        默认实现：整段生成后作为单个分片 yield，等价于非流式。
        支持真逐 token 的 provider（如 OpenAI 兼容接口）应覆写此方法，
        在异步生成器中逐块 yield 文本片段。

        system_blocks / user_prefix 语义同 generate（P1-1，可选）。
        """
        text = await self.generate(
            system=system,
            user=user,
            history=history,
            temperature=temperature,
            system_blocks=system_blocks,
            user_prefix=user_prefix,
        )
        if text:
            yield text
