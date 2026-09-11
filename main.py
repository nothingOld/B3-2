"""Git 변경 사항을 기반으로 Commit/PR 초안을 생성하는 CLI 프로그램."""

import argparse

from ai_client import call_ai_api
from git_utils import (
    get_git_status,
    get_staged_diff,
    get_unstaged_diff,
    is_git_repository,
)
from prompts import build_commit_prompt, build_pr_prompt


DEFAULT_MODEL = "gpt-5-mini"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 800


def parse_arguments() -> argparse.Namespace:
    """CLI 명령과 옵션을 파싱한다.

    Returns:
        파싱된 CLI 인자.
    """
    parser = argparse.ArgumentParser(
        description="Git 변경 사항 기반 Commit/PR 생성 도구"
    )

    parser.add_argument(
        "command",
        choices=["commit", "pr"],
        help="생성할 결과 유형",
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"사용할 AI 모델 (기본값: {DEFAULT_MODEL})",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"생성 다양성 (기본값: {DEFAULT_TEMPERATURE})",
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"최대 출력 토큰 수 (기본값: {DEFAULT_MAX_TOKENS})",
    )

    return parser.parse_args()


def build_prompt(
    command: str,
    status: str,
    unstaged_diff: str,
    staged_diff: str,
) -> str:
    """명령에 맞는 AI 프롬프트를 생성한다.

    Args:
        command: commit 또는 pr 명령.
        status: Git 변경 파일 목록.
        unstaged_diff: 스테이징되지 않은 변경 내용.
        staged_diff: 스테이징된 변경 내용.

    Returns:
        AI API에 전달할 프롬프트.
    """
    if command == "commit":
        return build_commit_prompt(
            status,
            unstaged_diff,
            staged_diff,
        )

    return build_pr_prompt(
        status,
        unstaged_diff,
        staged_diff,
    )


def main() -> None:
    """Git 변경 사항을 기반으로 AI 생성 결과를 출력한다."""
    args = parse_arguments()

    if not is_git_repository():
        print("[ERROR] 현재 디렉토리는 Git 저장소가 아닙니다.")
        return

    try:
        status = get_git_status()

        if not status:
            print("[INFO] 변경 사항이 없습니다.")
            return

        unstaged_diff = get_unstaged_diff()
        staged_diff = get_staged_diff()

        prompt = build_prompt(
            args.command,
            status,
            unstaged_diff,
            staged_diff,
        )

        print("[INFO] Git 변경 사항 수집 완료")
        print("[INFO] AI API 요청 중...")

        result = call_ai_api(
            prompt=prompt,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
    except RuntimeError as error:
        print(f"[ERROR] {error}")
        return

    print("[DONE] 생성 완료")
    print()
    print("--- Generated Result ---")
    print(result)
    print("------------------------")


if __name__ == "__main__":
    main()