"""
HTTP client for the vLLM OpenAI-compatible inference server.
"""

import os
from dataclasses import dataclass, field

import httpx


@dataclass
class VLLMClient:
    """
    Thin wrapper around the vLLM /v1/chat/completions endpoint.

    Configure via environment variables:
        VLLM_BASE_URL   — base URL of the running vLLM server (default: http://localhost:8000)
        VLLM_MODEL_NAME — model identifier to pass in requests
    """

    base_url: str = field(
        default_factory=lambda: os.getenv("VLLM_BASE_URL", "http://localhost:8000")
    )
    model_name: str = field(
        default_factory=lambda: os.getenv("VLLM_MODEL_NAME", "default")
    )

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """
        Send a chat completion request to the vLLM server.

        POSTs to {base_url}/v1/chat/completions using the OpenAI request format.
        If tools are provided, they are included in the request so the model
        can emit tool_call responses.

        Args:
            messages: List of OpenAI-format message dicts, each with 'role' and 'content'.
            tools: Optional list of OpenAI-format tool definitions (name, description,
                   parameters schema). Pass None for a plain chat completion.

        Returns:
            The parsed JSON response dict from the vLLM endpoint
            (contains 'choices', 'usage', etc.).

        Raises:
            httpx.HTTPStatusError: If the server returns a non-2xx response.
        """
        payload: dict = {"model": self.model_name, "messages": messages}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = httpx.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()
