"""ai_client 요청 payload 단위 테스트."""

import unittest

from ai_client import _build_payload


class AiClientPayloadTest(unittest.TestCase):
    """COPA 요청 파라미터 생성 테스트."""

    def test_default_temperature_is_omitted(self) -> None:
        """COPA 호환성을 위해 기본 temperature는 생략한다."""
        payload = _build_payload("hello", "gpt-5-mini", 1.0, 800)

        self.assertEqual(payload["max_tokens"], 800)
        self.assertNotIn("temperature", payload)

    def test_custom_temperature_is_sent(self) -> None:
        """사용자가 지정한 temperature는 실제 요청에 포함한다."""
        payload = _build_payload("hello", "gpt-5-mini", 0.3, 500)

        self.assertEqual(payload["temperature"], 0.3)
        self.assertEqual(payload["max_tokens"], 500)


if __name__ == "__main__":
    unittest.main()
