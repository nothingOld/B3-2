"""validators 모듈 단위 테스트."""

import unittest

from validators import validate_commit_result, validate_pr_result


class ValidatorsTest(unittest.TestCase):
    """Commit/PR 결과 검증 테스트."""

    def test_valid_commit_result(self) -> None:
        """정상 Commit 결과는 오류가 없어야 한다."""
        text = """COMMIT_TITLE: feat: API 호출 추가
COMMIT_BODY:
- ai_client.py에 API 호출 기능 추가
- main.py에 CLI 실행 흐름 추가
"""
        self.assertEqual(validate_commit_result(text), [])

    def test_valid_pr_result(self) -> None:
        """정상 PR 결과는 오류가 없어야 한다."""
        text = """PR_TITLE: feat: AI API 연동 추가
PR_BODY:
## Why
- 자동화를 위해 필요합니다.

## What
- API 연동을 추가했습니다.

## How to Test
- python main.py commit을 실행합니다.
"""
        self.assertEqual(validate_pr_result(text), [])

    def test_pr_without_section_fails(self) -> None:
        """필수 섹션이 없으면 오류가 발생해야 한다."""
        text = """PR_TITLE: feat: 테스트
PR_BODY:
## Why
- 이유
"""
        errors = validate_pr_result(text)
        self.assertIn("## What 섹션이 없습니다.", errors)
        self.assertIn("## How to Test 섹션이 없습니다.", errors)


if __name__ == "__main__":
    unittest.main()
