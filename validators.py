"""Commit 및 Pull Request 생성 결과 검증 기능을 제공한다."""


COMMIT_TITLE_PREFIX = "COMMIT_TITLE:"
COMMIT_BODY_MARKER = "COMMIT_BODY:"

PR_TITLE_PREFIX = "PR_TITLE:"
PR_BODY_MARKER = "PR_BODY:"

PR_SECTION_HEADERS = (
    "## Why",
    "## What",
    "## How to Test",
)

MAX_COMMIT_TITLE_LENGTH = 72
MAX_PR_TITLE_LENGTH = 80


def parse_commit_result(text: str) -> tuple[str, str]:
    """Commit 생성 결과에서 제목과 본문을 추출한다.

    Args:
        text: AI가 생성한 Commit 결과.

    Returns:
        Commit 제목과 본문.
    """
    lines = text.strip().splitlines()
    title = ""
    body_lines = []
    body_started = False

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith(COMMIT_TITLE_PREFIX):
            title = stripped_line.removeprefix(
                COMMIT_TITLE_PREFIX
            ).strip()
            continue

        if stripped_line == COMMIT_BODY_MARKER:
            body_started = True
            continue

        if body_started:
            body_lines.append(line)

    return title, "\n".join(body_lines).strip()


def parse_pr_result(text: str) -> tuple[str, str]:
    """PR 생성 결과에서 제목과 본문을 추출한다.

    Args:
        text: AI가 생성한 PR 결과.

    Returns:
        PR 제목과 본문.
    """
    lines = text.strip().splitlines()
    title = ""
    body_lines = []
    body_started = False

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith(PR_TITLE_PREFIX):
            title = stripped_line.removeprefix(
                PR_TITLE_PREFIX
            ).strip()
            continue

        if stripped_line == PR_BODY_MARKER:
            body_started = True
            continue

        if body_started:
            body_lines.append(line)

    return title, "\n".join(body_lines).strip()


def validate_commit_result(text: str) -> list[str]:
    """Commit 생성 결과의 형식을 검증한다.

    Args:
        text: AI가 생성한 Commit 결과.

    Returns:
        발견된 검증 오류 목록.
    """
    errors = []
    title, body = parse_commit_result(text)

    if not title:
        errors.append("커밋 제목이 없습니다.")
    elif len(title) > MAX_COMMIT_TITLE_LENGTH:
        errors.append(
            f"커밋 제목이 {MAX_COMMIT_TITLE_LENGTH}자를 초과했습니다."
        )

    if not body:
        errors.append("커밋 본문이 없습니다.")
        return errors

    bullet_count = sum(
        1
        for line in body.splitlines()
        if line.strip().startswith("- ")
    )

    if bullet_count < 1 or bullet_count > 2:
        errors.append(
            "커밋 본문은 1~2개의 불릿으로 작성해야 합니다."
        )

    return errors


def validate_pr_result(text: str) -> list[str]:
    """PR 생성 결과의 형식을 검증한다.

    Args:
        text: AI가 생성한 PR 결과.

    Returns:
        발견된 검증 오류 목록.
    """
    errors = []
    title, body = parse_pr_result(text)

    if not title:
        errors.append("PR 제목이 없습니다.")
    elif len(title) > MAX_PR_TITLE_LENGTH:
        errors.append(
            f"PR 제목이 {MAX_PR_TITLE_LENGTH}자를 초과했습니다."
        )

    if not body:
        errors.append("PR 본문이 없습니다.")
        return errors

    body_lines = body.splitlines()

    for index, header in enumerate(PR_SECTION_HEADERS):
        if header not in body_lines:
            errors.append(f"{header} 섹션이 없습니다.")
            continue

        start_index = body_lines.index(header) + 1

        if index + 1 < len(PR_SECTION_HEADERS):
            next_header = PR_SECTION_HEADERS[index + 1]

            if next_header in body_lines:
                end_index = body_lines.index(next_header)
            else:
                end_index = len(body_lines)
        else:
            end_index = len(body_lines)

        section_lines = body_lines[start_index:end_index]

        has_bullet = any(
            line.strip().startswith("- ")
            for line in section_lines
        )

        if not has_bullet:
            errors.append(
                f"{header} 섹션에 불릿이 없습니다."
            )

    return errors


def validate_result(
    command: str,
    text: str,
) -> list[str]:
    """명령 유형에 따라 AI 생성 결과를 검증한다.

    Args:
        command: commit 또는 pr 명령.
        text: AI가 생성한 결과.

    Returns:
        발견된 검증 오류 목록.
    """
    if command == "commit":
        return validate_commit_result(text)

    return validate_pr_result(text)