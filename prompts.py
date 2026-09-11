"""Commit 및 Pull Request 생성을 위한 AI 프롬프트를 제공한다."""


def build_commit_prompt(
    status: str,
    unstaged_diff: str,
    staged_diff: str,
) -> str:
    """Git 변경 사항을 기반으로 Commit 생성 프롬프트를 만든다.

    Args:
        status: Git 변경 파일 목록.
        unstaged_diff: 스테이징되지 않은 변경 내용.
        staged_diff: 스테이징된 변경 내용.

    Returns:
        Commit 메시지 생성을 위한 프롬프트.
    """
    return f"""
다음 Git 변경 사항을 분석하여 적절한 커밋 메시지를 작성하세요.

Git Status:
{status}

Unstaged Diff:
{unstaged_diff or "없음"}

Staged Diff:
{staged_diff or "없음"}
""".strip()


def build_pr_prompt(
    status: str,
    unstaged_diff: str,
    staged_diff: str,
) -> str:
    """Git 변경 사항을 기반으로 Pull Request 생성 프롬프트를 만든다.

    Args:
        status: Git 변경 파일 목록.
        unstaged_diff: 스테이징되지 않은 변경 내용.
        staged_diff: 스테이징된 변경 내용.

    Returns:
        Pull Request 초안 생성을 위한 프롬프트.
    """
    return f"""
다음 Git 변경 사항을 분석하여 Pull Request 제목과 본문을 작성하세요.

Git Status:
{status}

Unstaged Diff:
{unstaged_diff or "없음"}

Staged Diff:
{staged_diff or "없음"}
""".strip()