"""Codyssey COPA AI API 호출 기능을 제공한다."""

import os

import requests


API_URL = "https://copa.codyssey.kr/v1/chat/completions"


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

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            f"AI API 호출에 실패했습니다: {error}"
        ) from error

    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as error:
        raise RuntimeError(
            "AI API 응답 형식을 처리할 수 없습니다."
        ) from error

    return content.strip()