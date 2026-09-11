"""Codyssey COPA OpenAI 호환 API 호출 기능을 제공한다."""

import os
from typing import Any

import requests


API_URL = "https://copa.codyssey.kr/v1/chat/completions"
DEFAULT_PROVIDER_TEMPERATURE = 1.0
REQUEST_TIMEOUT_SECONDS = 60


def _get_api_key() -> str:
    """환경변수에서 AI API Key를 가져온다.

    Returns:
        AI API Key.

    Raises:
        RuntimeError: API Key가 설정되지 않은 경우.
    """
    api_key = os.getenv("AI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "AI_API_KEY 환경변수가 설정되지 않았습니다."
        )

    return api_key


def _build_payload(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    """COPA Chat Completions 요청 payload를 생성한다.

    Args:
        prompt: AI에게 전달할 프롬프트.
        model: 사용할 AI 모델.
        temperature: 생성 다양성 설정값.
        max_tokens: 최대 출력 토큰 수.

    Returns:
        Chat Completions 요청 payload.
    """
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": max_tokens,
    }

    # COPA의 gpt-5-mini는 기본 temperature 요청에서 오류가 발생할 수 있어
    # provider 기본값(1.0)은 필드를 생략하고, 사용자가 다른 값을 지정한
    # 경우에만 실제 API 파라미터로 전달한다.
    if temperature != DEFAULT_PROVIDER_TEMPERATURE:
        payload["temperature"] = temperature

    return payload


def _build_api_error(response: requests.Response) -> str:
    """HTTP 오류 응답을 사용자 메시지로 변환한다.

    Args:
        response: 실패한 HTTP 응답.

    Returns:
        상태 코드와 응답 본문을 포함한 오류 메시지.
    """
    response_body = response.text.strip()
    message = f"HTTP {response.status_code}"

    if response_body:
        message = f"{message}: {response_body}"

    if response.status_code == 502:
        message += (
            " (COPA 게이트웨이 또는 모델 파라미터 호환성을 확인하세요.)"
        )

    return message


def call_ai_api(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """COPA AI API를 호출하고 생성된 텍스트를 반환한다.

    Args:
        prompt: AI에게 전달할 프롬프트.
        model: 사용할 AI 모델.
        temperature: 생성 다양성 설정값.
        max_tokens: 최대 출력 토큰 수.

    Returns:
        AI가 생성한 텍스트.

    Raises:
        RuntimeError: API 호출 또는 응답 처리에 실패한 경우.
    """
    api_key = _get_api_key()
    payload = _build_payload(
        prompt,
        model,
        temperature,
        max_tokens,
    )

    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as error:
        raise RuntimeError(
            f"AI API 네트워크 요청에 실패했습니다: {error}"
        ) from error

    if not response.ok:
        raise RuntimeError(
            f"AI API 호출에 실패했습니다: {_build_api_error(response)}"
        )

    try:
        response_data = response.json()
        choice = response_data["choices"][0]
        content = choice["message"]["content"]
        finish_reason = choice.get("finish_reason")
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise RuntimeError(
            "AI API 응답 형식을 처리할 수 없습니다."
        ) from error

    if not isinstance(content, str) or not content.strip():
        reason_text = f" finish_reason={finish_reason}" if finish_reason else ""
        raise RuntimeError(
            "AI API가 빈 결과를 반환했습니다. "
            f"-max-tokens 값을 늘려보세요.{reason_text}"
        )

    return content.strip()
