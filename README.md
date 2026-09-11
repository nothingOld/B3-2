# B3-2 — AI 기반 Git Commit / PR Generator

Git 변경 사항을 수집해 Codyssey COPA의 OpenAI 호환 Chat Completions API로 전달하고, Commit 메시지와 Pull Request 초안을 자동 생성하는 Python CLI 도구입니다.

## 주요 기능

- `git status --short`, `git diff`, `git diff --staged` 결과 수집
- 변경 사항이 없으면 API를 호출하지 않고 종료
- `commit` 명령으로 Commit 제목/본문 생성
- `pr` 명령으로 PR 제목/본문 생성
- `-model`, `-temperature`, `-max-tokens` CLI 옵션
- Commit/PR 출력 형식 검증 및 최대 1회 재생성
- Safe Mode 민감정보 마스킹 및 diff 전송 제한
- Conventional Commit 기반 팀 컨벤션 적용
- API Key 환경변수 관리 및 요청 오류 처리

## 프로젝트 구조

```text
B3-2/
├── main.py                 # CLI와 전체 실행 흐름
├── git_utils.py            # Git status/diff 수집
├── ai_client.py            # COPA API 호출
├── prompts.py              # Commit/PR/보정 프롬프트
├── validators.py           # 생성 결과 파싱 및 검증
├── safe_mode.py            # 마스킹 및 diff 제한
├── conventions.py          # 팀 컨벤션 정의
├── tests/                  # 단위 테스트
├── BONUS1_EVIDENCE.md      # 실제 PR 제출 증빙 템플릿
├── SUBMISSION_CHECKLIST.md # 최종 제출 체크리스트
├── requirements.txt
└── .gitignore
```

## 개발 환경

- Python 3.10 이상
- Git
- macOS/Linux/Windows
- Codyssey COPA virtual key

## 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell에서는 다음과 같이 가상환경을 활성화합니다.

```powershell
.venv\Scripts\Activate.ps1
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

실제 API Key를 `.env`, README, Git commit에 포함하지 마세요.

## 기본 사용법

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

새로 생성한 untracked 파일은 `git status`에는 나타나지만 일반 `git diff`에 파일 내용이 포함되지 않습니다. 새 파일의 내용까지 AI가 분석해야 한다면 먼저 `git add`한 뒤 실행하면 `git diff --staged`로 수집됩니다.

## CLI 옵션

```bash
python main.py --help
```

| 옵션 | 기본값 | 설명 |
| --- | --- | --- |
| `-model`, `--model` | `gpt-5-mini` | 사용할 모델 |
| `-temperature`, `--temperature` | `1.0` | 생성 다양성(0.0~2.0) |
| `-max-tokens`, `--max-tokens` | `800` | 최대 출력 토큰 수 |
| `-safe-mode`, `--safe-mode` | off | 민감정보 마스킹/전송 제한 |
| `-max-files`, `--max-files` | `10` | Safe Mode 최대 파일 수 |
| `-max-lines`, `--max-lines` | `200` | Safe Mode 각 diff 최대 줄 수 |
| `-convention`, `--convention` | `conventional` | `none` 또는 `conventional` |

예시:

```bash
python main.py commit \
  -model gpt-5-mini \
  -temperature 1.0 \
  -max-tokens 800
```

### temperature 호환성 주의

COPA의 `gpt-5-mini`에서 기본 요청은 `model + messages` 형식으로 정상 동작하고 `max_tokens`도 사용할 수 있습니다. 일부 환경에서 `temperature` 필드를 명시하면 502가 발생할 수 있으므로 본 프로젝트는 기본값 `1.0`일 때 provider 기본값을 사용하도록 해당 필드를 생략합니다.

사용자가 기본값이 아닌 값을 지정하면 실제 API 요청에 `temperature`가 포함됩니다.

```bash
python main.py commit -temperature 0.3
```

해당 모델/게이트웨이가 custom temperature를 지원하지 않으면 API 오류가 표시됩니다. 이 경우 `-temperature 1.0`을 사용하거나 temperature를 지원하는 모델을 사용해야 합니다.

## Commit 출력 예시

```text
[INFO] Git 변경 사항 수집 완료
[INFO] AI API 요청 1/2
[DONE] 생성 완료

--- Commit Message ---
feat: Safe Mode 기반 Git diff 보호 기능 추가

- safe_mode.py에 민감정보 마스킹 기능 추가
- main.py에 Safe Mode CLI 옵션 연결
----------------------
```

검증 규칙:

- 제목 1줄 필수
- 제목 최대 72자, 50자 이내 권장
- 본문 1~2개 불릿
- 변경 파일 또는 모듈을 본문에서 언급하도록 프롬프트 구성

## PR 출력 예시

```text
--- PR Title ---
feat: Safe Mode 및 출력 검증 기능 추가

--- PR Body ---
## Why
- Git diff에 포함될 수 있는 민감정보를 보호하기 위해 필요합니다.

## What
- API Key와 이메일 마스킹을 추가했습니다.
- diff 파일/줄 수 제한을 추가했습니다.

## How to Test
- python main.py pr -safe-mode를 실행합니다.
----------------
```

검증 규칙:

- PR 제목 최대 80자
- `Why`, `What`, `How to Test` 필수
- 각 섹션 최소 1개의 불릿 필수

검증 실패 시 기존 결과와 오류 내용을 포함한 보정 프롬프트로 AI를 한 번만 재호출합니다. 따라서 1회 실행당 API 요청 횟수는 최대 2회입니다.

## Safe Mode — 기본 요구사항 + 보너스 3

Safe Mode를 켜면 다음 정책을 동시에 적용합니다.

1. `sk-...` 형태 API Key 마스킹
2. 이메일 주소 마스킹
3. Bearer token 마스킹
4. `api_key`, `access_token`, `secret`, `password` 형태 값 마스킹
5. Git status 최대 파일 수 제한
6. unstaged/staged diff 각각 최대 줄 수 제한

기본 정책:

```text
최대 파일 수: 10
각 diff 최대 줄 수: 200
```

실행:

```bash
python main.py commit -safe-mode
```

정책 변경:

```bash
python main.py pr -safe-mode -max-files 5 -max-lines 100
```

### Safe Mode OFF / ON 비교 예시

OFF:

```text
+ email=user@example.com
+ API_KEY=sk-abcdefghijklmnop1234
```

ON:

```text
+ email=[MASKED_EMAIL]
+ API_KEY=[MASKED_API_KEY]
```

## 팀 컨벤션 — 보너스 2

`conventional` 컨벤션에서는 제목을 다음 규칙으로 생성하도록 프롬프트를 강화합니다.

```text
<type>: <summary>
```

사용 가능한 type:

```text
feat / fix / docs / refactor / test / chore
```

실행:

```bash
python main.py commit -convention conventional
```

컨벤션 비활성화:

```bash
python main.py commit -convention none
```

### 적용 전/후 비교 예시

컨벤션 OFF:

```text
Git 변경 사항 수집 기능 추가
```

컨벤션 ON:

```text
feat: Git 변경 사항 수집 기능 추가
```

PR 제목에도 동일한 팀 컨벤션 규칙을 전달합니다.

## 보너스 1 — 실제 리포지토리에 적용

실제 PR 링크는 본인 GitHub 저장소 권한이 필요한 작업이므로 다음 절차로 수행합니다.

1. 이전 미션 GitHub 저장소를 선택합니다.
2. 기능/리팩토링/문서 개선용 브랜치를 만듭니다.
3. 의미 있는 변경을 수행합니다.
4. 본 도구로 Commit 초안을 생성합니다.
5. 생성 결과를 검토한 후 실제 commit을 작성합니다.
6. 본 도구로 PR 초안을 생성합니다.
7. GitHub에서 실제 PR을 생성합니다.
8. `BONUS1_EVIDENCE.md`에 PR 링크와 AI 초안 → 최종 PR 변경점 5~10줄을 기록합니다.

예시:

```bash
git switch -c feature/readme-improvement
python /path/to/B3-2/main.py commit -safe-mode
python /path/to/B3-2/main.py pr -safe-mode
```

## 테스트

API 호출 없이 로컬 단위 테스트를 실행할 수 있습니다.

```bash
python -m unittest discover -s tests -v
```

테스트 범위:

- Commit 결과 검증
- PR 필수 섹션/불릿 검증
- Safe Mode API Key/이메일 마스킹
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
- `git diff`에는 비밀번호, API Key, 개인정보가 들어갈 수 있으므로 외부 저장소 작업에서는 `-safe-mode` 사용을 권장합니다.
- `max_tokens`는 출력 토큰 상한입니다. 입력 토큰은 Git diff와 프롬프트 크기에 따라 별도로 사용됩니다.
- Safe Mode의 파일/줄 제한은 입력 토큰과 비용을 줄이는 데도 도움이 됩니다.
- 생성된 Commit/PR 문구는 최종 정답이 아니며 적용 전에 사용자가 검토해야 합니다.

## 최종 제출

GitHub에 다음 파일이 올라가 있는지 확인합니다.

```text
main.py
git_utils.py
ai_client.py
prompts.py
validators.py
safe_mode.py
conventions.py
requirements.txt
README.md
BONUS1_EVIDENCE.md
SUBMISSION_CHECKLIST.md
```

실제 API Key, `.venv`, `.env`, Python cache 파일은 push하지 않습니다.
