"""Safe Mode에서 AI에 전달할 Git diff 크기를 제한한다."""


MAX_DIFF_LINES = 200


def limit_diff(diff: str) -> str:
    """Git diff를 최대 200줄로 제한한다.

    Args:
        diff: git diff 출력.

    Returns:
        최대 200줄로 제한된 diff 문자열.
    """
    lines = diff.splitlines()

    if len(lines) <= MAX_DIFF_LINES:
        return diff

    limited_lines = lines[:MAX_DIFF_LINES]
    limited_lines.append("... [SAFE MODE] 이후 diff 내용은 생략했습니다.")
    return "\n".join(limited_lines)


def apply_safe_mode(
    unstaged_diff: str,
    staged_diff: str,
) -> tuple[str, str]:
    """unstaged/staged diff에 Safe Mode를 적용한다.

    Args:
        unstaged_diff: 스테이징되지 않은 diff.
        staged_diff: 스테이징된 diff.

    Returns:
        최대 200줄로 제한된 unstaged diff와 staged diff.
    """
    return limit_diff(unstaged_diff), limit_diff(staged_diff)
