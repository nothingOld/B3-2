# B3-2 — AI 기반 Git Commit / PR Generator

Git 변경 사항을 수집해 Codyssey COPA의 OpenAI 호환 Chat Completions API로 전달하고, Commit 메시지와 Pull Request 초안을 자동 생성하는 Python CLI 도구입니다.

## 주요 기능

- `git status --short`, `git diff`, `git diff --staged` 결과 수집
- 변경 사항이 없으면 API를 호출하지 않고 종료
- `commit` 명령으로 Commit 제목/본문 생성
- `pr` 명령으로 PR 제목/본문 생성
- `-model`, `-temperature`, `-max-tokens` CLI 옵션
- Commit/PR 출력 형식 검증 및 최대 1회 재생성
- `-safe-mode` 사용 시 AI에 전달하는 diff를 최대 200줄로 제한
- API Key 환경변수 관리 및 API 오류 처리

## 프로젝트 구조

```text
B3-2/
├── main.py          # CLI와 전체 실행 흐름
├── git_utils.py     # Git status/diff 수집
├── ai_client.py     # COPA API 호출
├── prompts.py       # Commit/PR/보정 프롬프트
├── validators.py    # 생성 결과 파싱 및 검증
├── safe_mode.py     # diff 전송량 제한
├── tests/           # 단위 테스트
├── requirements.txt
├── .env.example
└── .gitignore
```

## 개발 환경

- Python 3.10 이상
- Git
- Codyssey COPA virtual key

## 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## API Key 설정

API Key는 코드에 하드코딩하지 않고 `AI_API_KEY` 환경변수로 관리합니다.

macOS/Linux:

```bash
export AI_API_KEY="<virtual-key>"
```

Windows PowerShell:

```powershell
$env:AI_API_KEY="<virtual-key>"
```

실제 API Key를 README, 소스 코드, Git commit에 포함하지 마세요.

## 사용 방법

Commit 메시지 생성:

```bash
python main.py commit
```

PR 초안 생성:

```bash
python main.py pr
```

변경 사항이 없으면 다음과 같이 종료됩니다.

```text
[INFO] 변경 사항이 없습니다.
```

새로 생성한 untracked 파일은 `git status`에는 나타나지만 일반 `git diff`에는 파일 내용이 포함되지 않습니다. 새 파일의 내용까지 AI가 분석해야 한다면 먼저 `git add`한 뒤 실행하면 `git diff --staged`로 수집됩니다.

## CLI 옵션

```bash
python main.py --help
```

| 옵션 | 기본값 | 설명 |
| --- | --- | --- |
| `-model`, `--model` | `gpt-5-mini` | 사용할 AI 모델 |
| `-temperature`, `--temperature` | `1.0` | 생성 다양성(0.0~2.0) |
| `-max-tokens`, `--max-tokens` | `800` | 최대 출력 토큰 수 |
| `-safe-mode`, `--safe-mode` | off | 각 diff를 최대 200줄로 제한 |

예시:

```bash
python main.py commit \
  -model gpt-5-mini \
  -temperature 1.0 \
  -max-tokens 800
```

### temperature 호환성

COPA의 `gpt-5-mini`는 기본 요청에서 `temperature` 필드를 명시하면 502가 발생할 수 있어 기본값 `1.0`일 때는 provider 기본값을 사용하도록 필드를 생략합니다. 사용자가 다른 값을 지정하면 실제 API 요청에 `temperature`가 포함됩니다.

```bash
python main.py commit -temperature 0.3
```

해당 모델/게이트웨이가 custom temperature를 지원하지 않으면 API 오류가 출력될 수 있습니다.

## Commit 출력 예시

```text
[INFO] Git 변경 사항 수집 완료
[INFO] AI API 요청 1/2
[DONE] 생성 완료

--- Commit Message ---
Git 변경 사항 기반 커밋 메시지 생성 기능 추가

- main.py에 Commit 생성 CLI 흐름 추가
- ai_client.py에 AI API 호출 기능 추가
----------------------
```

검증 규칙:

- 제목 1줄 필수
- 제목 최대 72자, 50자 이내 권장
- 본문 1~2개 불릿

## PR 출력 예시

```text
--- PR Title ---
Git 변경 사항 기반 PR 초안 생성 기능 추가

--- PR Body ---
## Why
- PR 설명 작성 작업을 자동화하기 위해 필요합니다.

## What
- Git 변경 사항 수집 기능을 추가했습니다.
- AI API 기반 PR 초안 생성을 추가했습니다.

## How to Test
- python main.py pr 명령을 실행합니다.
----------------
```

검증 규칙:

- PR 제목 최대 80자
- `Why`, `What`, `How to Test` 필수
- 각 섹션 최소 1개의 불릿 필수

검증 실패 시 기존 결과와 오류 내용을 포함한 보정 프롬프트로 AI를 한 번만 재호출합니다. 따라서 1회 실행당 API 요청 횟수는 최대 2회입니다.

## Safe Mode

기본 요구사항의 민감정보/전송량 보호 기능으로 diff 전송량 제한 방식을 사용합니다.

```bash
python main.py commit -safe-mode
```

Safe Mode가 켜지면 unstaged diff와 staged diff를 각각 최대 200줄까지만 AI에 전달합니다. 이를 통해 큰 diff나 민감정보가 포함될 가능성이 있는 전체 변경 내용을 그대로 보내는 것을 줄일 수 있습니다.

## 테스트

API 호출 없이 단위 테스트를 실행할 수 있습니다.

```bash
python -m unittest discover -s tests -v
```

테스트 범위:

- Commit 결과 검증
- PR 필수 섹션/불릿 검증
- Safe Mode diff 줄 수 제한
- `max_tokens` payload 적용
- custom `temperature` payload 적용

## 오류 처리

### API Key 미설정

```text
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
```

### Git 저장소가 아닌 경우

```text
[ERROR] 현재 디렉토리는 Git 저장소가 아닙니다.
```

### API 호출 실패

HTTP 상태 코드와 가능한 응답 본문을 출력합니다. 502인 경우 COPA 게이트웨이 또는 모델 파라미터 호환성을 확인하라는 메시지도 제공합니다.

### 생성 결과 형식 실패

최초 생성 결과가 검증 규칙을 만족하지 않으면 한 번 재생성합니다. 두 번째 결과도 실패하면 오류 원인을 출력하고 종료합니다.

## 보안 및 비용 주의사항

- API Key는 반드시 환경변수로 관리합니다.
- `.env`는 `.gitignore`에 포함되어 있습니다.
- `git diff`에는 비밀번호, API Key, 개인정보 등이 포함될 수 있으므로 외부 전송 전에 변경 내용을 확인하거나 `-safe-mode`를 사용하세요.
- `max_tokens`는 출력 토큰 상한입니다. 입력 토큰은 Git diff와 프롬프트 크기에 따라 별도로 사용됩니다.
- 생성된 Commit/PR 문구는 적용 전에 사용자가 검토해야 합니다.
