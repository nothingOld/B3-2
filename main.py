"""Git 변경 사항을 기반으로 Commit/PR 초안을 생성하는 CLI 프로그램."""

import argparse

from ai_client import DEFAULT_PROVIDER_TEMPERATURE, call_ai_api
from conventions import SUPPORTED_CONVENTIONS, get_convention_rules
from git_utils import (
    get_git_status,
    get_staged_diff,
    get_unstaged_diff,
    is_git_repository,
)
from prompts import (
    build_commit_prompt,
    build_correction_prompt,
    build_pr_prompt,
)
from safe_mode import (
    DEFAULT_MAX_FILES,
    DEFAULT_MAX_LINES,
    apply_safe_mode,
)
from validators import (
    parse_commit_result,
    parse_pr_result,
    validate_result,
)


DEFAULT_MODEL = "gpt-5-mini"
DEFAULT_TEMPERATURE = DEFAULT_PROVIDER_TEMPERATURE
DEFAULT_MAX_TOKENS = 800


def _temperature(value: str) -> float:
    """CLI temperature 값을 검증한다.

    Args:
        value: CLI에서 전달된 문자열.

    Returns:
        0.0~2.0 범위의 실수.

    Raises:
        argparse.ArgumentTypeError: 범위를 벗어난 경우.
    """
    temperature = float(value)

    if not 0.0 <= temperature <= 2.0:
        raise argparse.ArgumentTypeError(
            "temperature는 0.0 이상 2.0 이하이어야 합니다."
        )

    return temperature


def _positive_integer(value: str) -> int:
    """CLI 양의 정수 값을 검증한다.

    Args:
        value: CLI에서 전달된 문자열.

    Returns:
        1 이상의 정수.

    Raises:
        argparse.ArgumentTypeError: 양의 정수가 아닌 경우.
    """
    number = int(value)

    if number < 1:
        raise argparse.ArgumentTypeError("1 이상의 정수를 입력하세요.")

    return number


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
        "-model",
        "--model",
        default=DEFAULT_MODEL,
        help=f"사용할 AI 모델 (기본값: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "-temperature",
        "--temperature",
        type=_temperature,
        default=DEFAULT_TEMPERATURE,
        help=f"생성 다양성 (기본값: {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "-max-tokens",
        "--max-tokens",
        type=_positive_integer,
        default=DEFAULT_MAX_TOKENS,
        help=f"최대 출력 토큰 수 (기본값: {DEFAULT_MAX_TOKENS})",
    )
    parser.add_argument(
        "-safe-mode",
        "--safe-mode",
        action="store_true",
        help="민감정보 마스킹 및 diff 전송 제한 적용",
    )
    parser.add_argument(
        "-max-files",
        "--max-files",
        type=_positive_integer,
        default=DEFAULT_MAX_FILES,
        help=f"Safe Mode 최대 파일 수 (기본값: {DEFAULT_MAX_FILES})",
    )
    parser.add_argument(
        "-max-lines",
        "--max-lines",
        type=_positive_integer,
        default=DEFAULT_MAX_LINES,
        help=f"Safe Mode 최대 diff 줄 수 (기본값: {DEFAULT_MAX_LINES})",
    )
    parser.add_argument(
        "-convention",
        "--convention",
        choices=SUPPORTED_CONVENTIONS,
        default="conventional",
        help="Commit/PR 팀 컨벤션 (기본값: conventional)",
    )

    return parser.parse_args()


def build_prompt(
    command: str,
    status: str,
    unstaged_diff: str,
    staged_diff: str,
    convention_rules: str,
) -> str:
    """명령에 맞는 AI 프롬프트를 생성한다.

    Args:
        command: commit 또는 pr 명령.
        status: Git 변경 파일 목록.
        unstaged_diff: 스테이징되지 않은 변경 내용.
        staged_diff: 스테이징된 변경 내용.
        convention_rules: 팀 컨벤션 규칙.

    Returns:
        AI API에 전달할 프롬프트.
    """
    if command == "commit":
        return build_commit_prompt(
            status,
            unstaged_diff,
            staged_diff,
            convention_rules,
        )

    return build_pr_prompt(
        status,
        unstaged_diff,
        staged_diff,
        convention_rules,
    )


def generate_result(
    args: argparse.Namespace,
    prompt: str,
    convention_rules: str,
) -> str:
    """AI 결과를 생성하고 형식을 검증한다.

    Args:
        args: CLI 인자.
        prompt: 최초 생성 프롬프트.
        convention_rules: 팀 컨벤션 규칙.

    Returns:
        형식 검증을 통과한 AI 생성 결과.

    Raises:
        RuntimeError: 두 번째 생성 결과도 검증에 실패한 경우.
    """
    print("[INFO] AI API 요청 1/2")
    result = call_ai_api(
        prompt=prompt,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    errors = validate_result(args.command, result)

    if not errors:
        return result

    print("[WARN] 생성 결과 형식 검증 실패")
    print("[INFO] AI API 재요청 2/2")
    correction_prompt = build_correction_prompt(
        args.command,
        result,
        errors,
        convention_rules,
    )
    corrected_result = call_ai_api(
        prompt=correction_prompt,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    remaining_errors = validate_result(
        args.command,
        corrected_result,
    )

    if remaining_errors:
        error_message = ", ".join(remaining_errors)
        raise RuntimeError(
            f"생성 결과 형식 검증에 실패했습니다: {error_message}"
        )

    return corrected_result


def print_result(command: str, result: str) -> None:
    """검증된 생성 결과를 터미널에 출력한다.

    Args:
        command: commit 또는 pr 명령.
        result: 검증된 AI 생성 결과.
    """
    if command == "commit":
        title, body = parse_commit_result(result)
        print()
        print("--- Commit Message ---")
        print(title)

        if body:
            print()
            print(body)

        print("----------------------")
        return

    title, body = parse_pr_result(result)
    print()
    print("--- PR Title ---")
    print(title)
    print()
    print("--- PR Body ---")
    print(body)
    print("----------------")


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

        if args.safe_mode:
            status, unstaged_diff, staged_diff = apply_safe_mode(
                status,
                unstaged_diff,
                staged_diff,
                args.max_files,
                args.max_lines,
            )
            print(
                "[INFO] Safe Mode 적용: "
                f"최대 {args.max_files}개 파일, "
                f"각 diff 최대 {args.max_lines}줄"
            )

        convention_rules = get_convention_rules(args.convention)
        prompt = build_prompt(
            args.command,
            status,
            unstaged_diff,
            staged_diff,
            convention_rules,
        )

        print("[INFO] Git 변경 사항 수집 완료")
        result = generate_result(
            args,
            prompt,
            convention_rules,
        )
    except (RuntimeError, ValueError) as error:
        print(f"[ERROR] {error}")
        return

    print("[DONE] 생성 완료")
    print_result(args.command, result)


if __name__ == "__main__":
    main()
