"""Git 변경 사항을 수집하고 출력하는 CLI 프로그램."""

from git_utils import (
    get_git_status,
    get_staged_diff,
    get_unstaged_diff,
    is_git_repository,
)


def print_git_changes(
    status: str,
    unstaged_diff: str,
    staged_diff: str,
) -> None:
    """수집된 Git 변경 사항을 출력한다.

    Args:
        status: Git 변경 파일 목록.
        unstaged_diff: 스테이징되지 않은 변경 내용.
        staged_diff: 스테이징된 변경 내용.
    """
    print("[INFO] Git status 수집 완료")
    print()
    print("--- Git Status ---")
    print(status)

    print()
    print("[INFO] Git diff 수집 완료")
    print()
    print("--- Unstaged Diff ---")
    print(unstaged_diff or "스테이징되지 않은 변경 내용이 없습니다.")

    print()
    print("--- Staged Diff ---")
    print(staged_diff or "스테이징된 변경 내용이 없습니다.")


def main() -> None:
    """Git 변경 사항을 수집하고 출력한다."""
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
    except RuntimeError as error:
        print(f"[ERROR] {error}")
        return

    print_git_changes(
        status,
        unstaged_diff,
        staged_diff,
    )


if __name__ == "__main__":
    main()