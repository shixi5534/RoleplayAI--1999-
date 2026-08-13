"""统一异常体系（业务异常与 HTTP 状态码解耦）。

所有自定义异常继承自 RoleplayError；API 层通过 handlers 统一序列化为
{ "error": { "code", "message", "details" } } 结构，前端无需关心具体异常类型。
"""


class RoleplayError(Exception):
    """所有业务异常的基类。"""

    code: str = "internal_error"
    status_code: int = 500

    def __init__(self, message: str, *, details: object | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationError(RoleplayError):
    code = "validation_error"
    status_code = 422


class NotFoundError(RoleplayError):
    code = "not_found"
    status_code = 404


class ConfigurationError(RoleplayError):
    code = "configuration_error"
    status_code = 500


class ProviderError(RoleplayError):
    """LLM / 外部服务调用失败。"""

    code = "provider_error"
    status_code = 502


class EmotionError(RoleplayError):
    code = "emotion_error"
    status_code = 500
