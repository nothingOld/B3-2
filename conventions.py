"""Commit 및 Pull Request 팀 컨벤션을 정의한다."""


SUPPORTED_CONVENTIONS = ("none", "conventional")

_CONVENTIONAL_RULES = """
팀 컨벤션:
- 제목은 `<type>: <summary>` 형식을 사용합니다.
- type은 feat, fix, docs, refactor, test, chore 중 하나를 사용합니다.
- 새로운 기능은 feat, 버그 수정은 fix, 문서는 docs를 사용합니다.
- 동작 변경 없는 구조 개선은 refactor를 사용합니다.
- 테스트 변경은 test, 설정/빌드/기타 작업은 chore를 사용합니다.
""".strip()


def get_convention_rules(convention: str) -> str:
    """선택된 컨벤션의 프롬프트 규칙을 반환한다.

    Args:
        convention: 컨벤션 이름.

    Returns:
        AI 프롬프트에 포함할 컨벤션 규칙. none이면 빈 문자열.

    Raises:
        ValueError: 지원하지 않는 컨벤션인 경우.
    """
    if convention == "none":
        return ""

    if convention == "conventional":
        return _CONVENTIONAL_RULES

    raise ValueError(f"지원하지 않는 컨벤션입니다: {convention}")
