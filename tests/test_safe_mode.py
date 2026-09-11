"""safe_mode 모듈 단위 테스트."""

import unittest

from safe_mode import limit_diff, mask_sensitive_data


class SafeModeTest(unittest.TestCase):
    """Safe Mode 마스킹 및 제한 테스트."""

    def test_masks_email_and_api_key(self) -> None:
        """이메일과 API Key를 마스킹해야 한다."""
        text = "email=user@example.com key=sk-abcdefghijklmnop1234"
        masked = mask_sensitive_data(text)

        self.assertNotIn("user@example.com", masked)
        self.assertNotIn("sk-abcdefghijklmnop1234", masked)
        self.assertIn("[MASKED_EMAIL]", masked)
        self.assertIn("[MASKED_API_KEY]", masked)

    def test_limits_diff_lines(self) -> None:
        """diff 줄 수가 설정값을 넘지 않도록 제한해야 한다."""
        diff = "\n".join(f"line-{index}" for index in range(20))
        limited = limit_diff(diff, max_files=10, max_lines=5)

        self.assertIn("line-4", limited)
        self.assertNotIn("line-5", limited)
        self.assertIn("[SAFE MODE]", limited)


if __name__ == "__main__":
    unittest.main()
