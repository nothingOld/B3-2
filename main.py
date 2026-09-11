"""Git 변경 사항을 수집하는 CLI 프로그램."""

import subprocess


def run_git_command(command: list[str]) -> str:
    """Git 명령어를 실행하고 표준 출력을 반환한다.

    Args:
        command: 실행할 Git 명령어와 인자의 목록.

    Returns:
        Git 명령어의 표준 출력.

    Raises:
        RuntimeError: Git 명령어 실행에 실패한 경우.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        error_message = error.stderr.strip()

        raise RuntimeError(
            f"Git 명령 실행에 실패했습니다: {error_message}"
        ) from error

    return result.stdout.strip()


def is_git_repository() -> bool:
    """현재 디렉토리가 Git 저장소인지 확인한다.

    Returns:
        Git 저장소이면 True, 아니면 False.
    """
    try:
        result = run_git_command(
            ["git", "rev-parse", "--is-inside-work-tree"]
        )
    except RuntimeError:
        return False

    return result == "true"


def get_git_status() -> str:
    """Git 변경 파일 목록을 반환한다.

    Returns:
        git status --short 명령의 출력.
    """
    return run_git_command(["git", "status", "--short"])


def get_unstaged_diff() -> str:
    """스테이징되지 않은 Git 변경 내용을 반환한다.

    Returns:
        git diff 명령의 출력.
    """
    return run_git_command(["git", "diff"])


def get_staged_diff() -> str:
    """스테이징된 Git 변경 내용을 반환한다.

    Returns:
        git diff --staged 명령의 출력.
    """
    return run_git_command(["git", "diff", "--staged"])


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


if __name__ == "__main__":
    main()