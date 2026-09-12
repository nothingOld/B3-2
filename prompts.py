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
다음 Git 변경 사항을 분석하여 커밋 메시지를 작성하세요.

반드시 다음 형식으로만 출력하세요.

COMMIT_TITLE: 커밋 제목
COMMIT_BODY:
- 핵심 변경 사항
- 핵심 변경 사항

규칙:
- 커밋 제목은 반드시 한 줄로 작성합니다.
- 커밋 제목은 최대 72자이며 가능하면 50자 이내로 작성합니다.
- 커밋 본문은 1~2개의 불릿으로 작성합니다.
- 변경된 파일 또는 모듈을 본문에 1개 이상 언급합니다.
- 실제 Git 변경 내용만 근거로 작성합니다.
- 설명, 인사말, 코드 블록을 추가하지 않습니다.

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
다음 Git 변경 사항을 분석하여 Pull Request 초안을 작성하세요.

반드시 다음 형식으로만 출력하세요.

PR_TITLE: PR 제목
PR_BODY:
## Why
- 변경 배경

## What
- 핵심 변경 사항

## How to Test
- 테스트 방법

규칙:
- PR 제목은 반드시 한 줄이며 최대 80자입니다.
- Why, What, How to Test 섹션을 반드시 포함합니다.
- 각 섹션에는 최소 1개의 불릿을 포함합니다.
- 실제 Git 변경 내용만 근거로 작성합니다.
- 설명, 인사말, 코드 블록을 추가하지 않습니다.

Git Status:
{status}

Unstaged Diff:
{unstaged_diff or "없음"}

Staged Diff:
{staged_diff or "없음"}
""".strip()


def build_correction_prompt(
    command: str,
    generated_text: str,
    errors: list[str],
) -> str:
    """형식 검증에 실패한 결과의 보정 프롬프트를 만든다.

    Args:
        command: commit 또는 pr 명령.
        generated_text: 기존 AI 생성 결과.
        errors: 형식 검증 오류 목록.

    Returns:
        형식 수정 요청 프롬프트.
    """
    error_text = "\n".join(f"- {error}" for error in errors)

    if command == "commit":
        format_rule = """
COMMIT_TITLE: 커밋 제목
COMMIT_BODY:
- 핵심 변경 사항
- 핵심 변경 사항

규칙:
- 제목은 한 줄이며 최대 72자
- 본문은 1~2개의 불릿
""".strip()
    else:
        format_rule = """
PR_TITLE: PR 제목
PR_BODY:
## Why
- 변경 배경

## What
- 핵심 변경 사항

## How to Test
- 테스트 방법

규칙:
- 제목은 한 줄이며 최대 80자
- 세 개의 섹션 필수
- 각 섹션에 최소 1개의 불릿 필수
""".strip()

    return f"""
다음 생성 결과가 형식 검증에 실패했습니다.

검증 오류:
{error_text}

기존 생성 결과:
{generated_text}

다음 형식에 맞게 다시 작성하세요.

{format_rule}

기존 내용의 의미는 유지하고 결과만 출력하세요.
""".strip()
