"""LLM client — every agent gets its model from here, always via the LiteLLM gateway."""

from langchain_openai import ChatOpenAI

from stakagents.core.config import settings

# The LiteLLM proxy has no master key in local dev, but the OpenAI-compatible
# client still requires a non-empty api_key, so we pass a harmless placeholder.
_GATEWAY_API_KEY = "sk-noop"


def get_chat_model(
    model: str = "gemini-flash",
    temperature: float = 0.0,
    **kwargs,
) -> ChatOpenAI:
    """Return a LangChain chat model pointed at the LiteLLM gateway.

    `model` must match a `model_name` in litellm.config.yaml. Swapping providers
    later (e.g. gemini-flash -> a paid `claude-*` entry) is just a different
    string here — no agent code changes.
    """
    return ChatOpenAI(
        model=model,
        base_url=f"{settings.litellm_base_url}/v1",
        api_key=_GATEWAY_API_KEY,
        temperature=temperature,
        **kwargs,
    )
