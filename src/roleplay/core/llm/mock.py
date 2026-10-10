"""Mock LLM Provider —— 离线可用、确定性回复，用于演示与测试。

⚠️ 历史回显默认关闭（P0-A 修复）
--------------------------------
本 provider 曾无条件把最近 6 条历史**原样拼进回复**：

    tail = "｜稍早的对话：" + "；".join(f"{role}：「{content}」" for h in history[-6:])

而该回复经 orchestrator 又被 ``SessionMemory.append_many()`` 写回历史，下一轮再被
拼进新回复 —— 形成 **自我复制正反馈**：回复长度 ≈ 常数 + ×(1 + 6/轮长)。

实测（默认 mock，单会话）：
    6 轮   3,418 字符
    10 轮  43,210 字符
    22 轮  65,700,000 字符
    52 轮  **777,000,000 字符**（单次响应 872MB，进程内存 7.3GB）
    增长率收敛 ×1.84/轮（指数）
对照实验（注入不回显历史的 LLM）：30 轮仅 890 字符，×1.04（线性）。
=> 指数膨胀是「mock 回显 × 历史持久化」的**乘积效应**，真实 provider 不受影响。

因此默认 ``echo_history=False``：``generate()`` 只回显本轮用户输入，回复是
确定性常数长度，便于断言，也切断了正反馈。演示/测试若需要旧的「记得聊过什么」
效果，显式传 ``echo_history=True`` 恢复原行为。
"""
from .base import LLMPort


class MockLLMProvider(LLMPort):
    def __init__(self, model: str = "mock-model", echo_history: bool = False) -> None:
        self._model = model
        # P0-A：默认 False（关闭历史回显）——开启会让回复随历史自我复制、指数膨胀。
        self._echo_history = echo_history

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
        system_blocks: list[str] | None = None,
        user_prefix: str | None = None,
    ) -> str:
        # 不调用任何外部服务：回显用户原文 + 角色扮演提示，便于断言与演示。
        # P1-1 的 system_blocks / user_prefix 在此被忽略（mock 不区分消息结构），
        # 仅接受参数以保持 LLMPort 契约一致。
        #
        # history 默认**不参与生成**（见模块 docstring：回显会造成指数膨胀）。
        tail = ""
        if self._echo_history and history:
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
        system_blocks: list[str] | None = None,
        user_prefix: str | None = None,
    ):
        # 离线逐片段产出，便于演示打字机/流式效果（约 12 片）。
        text = await self.generate(
            system=system,
            user=user,
            history=history,
            temperature=temperature,
            system_blocks=system_blocks,
            user_prefix=user_prefix,
        )
        if not text:
            return
        step = max(1, len(text) // 12)
        for i in range(0, len(text), step):
            yield text[i : i + step]
