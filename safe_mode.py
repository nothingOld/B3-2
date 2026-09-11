"""AI 전송 전 Git 변경 내용의 민감정보와 크기를 제한한다."""

import re


DEFAULT_MAX_FILES = 10
DEFAULT_MAX_LINES = 200

_EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)
_OPENAI_KEY_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")
_BEARER_TOKEN_PATTERN = re.compile(
    r"(?i)(authorization\s*[:=]\s*bearer\s+)[A-Za-z0-9._~-]+"
)
_SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)((?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*)"
    r"([^\s,;]+)"
)
_DIFF_HEADER = "diff --git "


def mask_sensitive_data(text: str) -> str:
    """텍스트에 포함된 대표적인 민감정보를 마스킹한다.

    Args:
        text: 마스킹할 텍스트.

    Returns:
        민감정보가 마스킹된 텍스트.
    """
    masked_text = _OPENAI_KEY_PATTERN.sub("[MASKED_API_KEY]", text)
    masked_text = _EMAIL_PATTERN.sub("[MASKED_EMAIL]", masked_text)
    masked_text = _BEARER_TOKEN_PATTERN.sub(
        r"\1[MASKED_TOKEN]",
        masked_text,
    )
    masked_text = _SECRET_ASSIGNMENT_PATTERN.sub(
        r"\1[MASKED_SECRET]",
        masked_text,
    )
    return masked_text


def limit_status(status: str, max_files: int) -> str:
    """Git status 출력의 파일 수를 제한한다.

    Args:
        status: git status --short 출력.
        max_files: 최대 파일 수.

    Returns:
        제한된 status 문자열.
    """
    lines = status.splitlines()

    if len(lines) <= max_files:
        return status

    omitted_count = len(lines) - max_files
    limited_lines = lines[:max_files]
    limited_lines.append(
        f"... [SAFE MODE] {omitted_count}개 파일 항목 생략"
    )
    return "\n".join(limited_lines)


def limit_diff(diff: str, max_files: int, max_lines: int) -> str:
    """Git diff의 파일 수와 전체 줄 수를 제한한다.

    Args:
        diff: git diff 출력.
        max_files: 최대 diff 파일 수.
        max_lines: 최대 diff 줄 수.

    Returns:
        제한된 diff 문자열.
    """
    if not diff:
        return ""

    selected_lines = []
    file_count = 0

    for line in diff.splitlines():
        if line.startswith(_DIFF_HEADER):
            file_count += 1
            if file_count > max_files:
                break

        selected_lines.append(line)

        if len(selected_lines) >= max_lines:
            break

    was_truncated = len(selected_lines) < len(diff.splitlines())

    if was_truncated:
        selected_lines.append(
            "... [SAFE MODE] diff 전송 범위를 제한했습니다."
        )

    return "\n".join(selected_lines)


def apply_safe_mode(
    status: str,
    unstaged_diff: str,
    staged_diff: str,
    max_files: int,
    max_lines: int,
) -> tuple[str, str, str]:
    """Git 컨텍스트에 Safe Mode 정책을 적용한다.

    Args:
        status: Git 변경 파일 목록.
        unstaged_diff: 스테이징되지 않은 diff.
        staged_diff: 스테이징된 diff.
        max_files: 전송할 최대 파일 수.
        max_lines: 각 diff에서 전송할 최대 줄 수.

    Returns:
        Safe Mode가 적용된 status, unstaged diff, staged diff.
    """
    safe_status = mask_sensitive_data(limit_status(status, max_files))
    safe_unstaged_diff = mask_sensitive_data(
        limit_diff(unstaged_diff, max_files, max_lines)
    )
    safe_staged_diff = mask_sensitive_data(
        limit_diff(staged_diff, max_files, max_lines)
    )

    return safe_status, safe_unstaged_diff, safe_staged_diff
