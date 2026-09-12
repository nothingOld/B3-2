# B3-2 — AI 기반 Git Commit / PR Generator

Git 변경 사항을 자동으로 수집한 뒤 Codyssey COPA의 OpenAI 호환 Chat Completions API에 전달하여 **Commit 메시지**와 **Pull Request 초안**을 생성하는 Python CLI 도구입니다.

이 프로젝트는 `git status`, `git diff`, `git diff --staged` 결과를 Python에서 수집하고, 변경 맥락을 프롬프트로 구성해 AI가 일관된 형식의 Commit/PR 초안을 작성하도록 합니다. 생성 결과는 정해진 형식에 맞는지 검증하며, 형식이 맞지 않으면 최대 1회 보정 요청을 수행합니다.

> 이 프로그램은 Commit 메시지와 PR 초안을 **생성하여 터미널에 출력하는 도구**입니다.  
> 실제 `git commit`, `git push`, GitHub PR 생성은 자동으로 수행하지 않습니다.

---

## 1. 주요 기능

- `git status --short`로 변경된 파일 목록 수집
- `git diff`로 **unstaged** 변경 내용 수집
- `git diff --staged`로 **staged** 변경 내용 수집
- 변경 사항이 없으면 AI API를 호출하지 않고 종료
- `commit` 명령으로 Commit 제목/본문 생성
- `pr` 명령으로 PR 제목/본문 생성
- `-model`, `-temperature`, `-max-tokens` 옵션 지원
- Commit/PR 생성 결과 형식 검증
- 형식 검증 실패 시 최대 1회 AI 재요청
- `-safe-mode` 사용 시 AI에 전달하는 diff 크기 제한
- API Key를 환경변수로 관리
- Git/API/응답 형식 오류 처리

---

## 2. 전체 동작 흐름

```text
사용자가 파일 수정
        ↓
git status / git diff / git diff --staged
        ↓
Python subprocess로 Git 결과 수집
        ↓
commit 또는 pr 프롬프트 구성
        ↓
Codyssey COPA Chat Completions API 호출
        ↓
AI 생성 결과 수신
        ↓
형식 검증
        ↓
검증 실패 시 최대 1회 재요청
        ↓
Commit 메시지 또는 PR 초안 출력
```

---

## 3. 프로젝트 구조

```text
B3-2/
├── main.py
├── git_utils.py
├── ai_client.py
├── prompts.py
├── validators.py
├── safe_mode.py
├── requirements.txt
├── .gitignore
└── README.md
```

### 파일별 역할

| 파일 | 역할 |
| --- | --- |
| `main.py` | CLI 옵션 처리 및 전체 실행 흐름 제어 |
| `git_utils.py` | Git 저장소 확인, status/diff 수집 |
| `ai_client.py` | COPA API 요청 및 응답/오류 처리 |
| `prompts.py` | Commit, PR, 보정용 프롬프트 생성 |
| `validators.py` | AI 생성 결과 파싱 및 형식 검증 |
| `safe_mode.py` | AI에 전달할 diff 크기 제한 |
| `requirements.txt` | 외부 Python 패키지 목록 |
| `.gitignore` | Git에 포함하지 않을 파일 지정 |

---

## 4. 개발 환경

- Python **3.10 이상**
- Git
- Codyssey COPA virtual key
- 외부 Python 패키지
  - `requests==2.32.5`

Python과 Git 버전 확인:

```bash
python3 --version
git --version
```

---

## 5. 설치

프로젝트 폴더로 이동합니다.

```bash
cd B3-2
```

필요한 패키지를 설치합니다.

```bash
python3 -m pip install -r requirements.txt
```

`requirements.txt`에는 외부 라이브러리인 `requests`만 포함되어 있습니다.

### 가상환경 사용은 선택 사항

가상환경은 미션 수행에 필수는 아니지만, 다른 Python 프로젝트와 패키지 충돌을 방지하려면 사용할 수 있습니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

---

## 6. API Key 설정

API Key는 코드에 직접 작성하지 않고 `AI_API_KEY` 환경변수에서 읽습니다.

macOS/Linux:

```bash
export AI_API_KEY="<virtual-key>"
```

설정 여부 확인:

```bash
python -c "import os; print('설정 완료' if os.getenv('AI_API_KEY') else '미설정')"
```

> 실제 virtual key를 README, Python 코드, Git commit에 포함하지 마세요.

현재 `.gitignore`는 `.env`, `.env.*`, `.venv/`, `__pycache__/`, `*.pyc` 등을 Git 추적 대상에서 제외합니다.

---

## 7. Git 변경 사항 준비

이 프로그램은 **Git 저장소 내부에서 실행**해야 합니다.

아직 Git 저장소가 아니라면:

```bash
git init -b main
```

현재 변경 상태 확인:

```bash
git status --short
```

예:

```text
 M main.py
?? new_file.py
```

### `git add` 전과 후의 차이

파일을 수정하고 아직 `git add`하지 않았다면 변경 내용은 주로:

```bash
git diff
```

에서 확인됩니다.

`git add`한 뒤에는:

```bash
git diff --staged
```

에서 확인됩니다.

이 프로그램은 **둘 다 수집**하므로 staged/unstaged 상태 모두 처리할 수 있습니다.

단, 새로 만든 **untracked 파일(`??`)** 은 `git status`에는 나타나지만 일반 `git diff`에는 파일 내용이 포함되지 않습니다. 새 파일 내용까지 AI가 분석하게 하려면 먼저:

```bash
git add <파일명>
```

또는:

```bash
git add .
```

을 실행한 뒤 도구를 사용하는 것이 좋습니다.

---

## 8. 기본 사용법

### Commit 메시지 생성

```bash
python main.py commit
```

실행 흐름:

```text
Git 변경 사항 확인
→ Commit용 프롬프트 생성
→ AI API 호출
→ 결과 검증
→ Commit 메시지 출력
```

### PR 초안 생성

```bash
python main.py pr
```

실행 흐름:

```text
Git 변경 사항 확인
→ PR용 프롬프트 생성
→ AI API 호출
→ 결과 검증
→ PR 제목/본문 출력
```

### 변경 사항이 없는 경우

```text
[INFO] 변경 사항이 없습니다.
```

이 경우 API는 호출하지 않습니다.

---

## 9. CLI 옵션

전체 옵션 확인:

```bash
python main.py --help
```

현재 지원하는 옵션:

| 옵션 | 기본값 | 설명 |
| --- | --- | --- |
| `-model`, `--model` | `gpt-5.4-mini` | 사용할 AI 모델 |
| `-temperature`, `--temperature` | `1.0` | 생성 다양성, `0.0 ~ 2.0` |
| `-max-tokens`, `--max-tokens` | `commit: 800`, `pr: 2000` | 최대 출력 토큰 수 |
| `-safe-mode`, `--safe-mode` | off | AI에 전달하는 diff 크기 제한 |

옵션 순서는 자유롭게 사용할 수 있습니다.

예:

```bash
python main.py commit \
  -model gpt-5.4-mini \
  -temperature 0.3 \
  -max-tokens 1200 \
  -safe-mode
```

---

## 10. `-model`

기본 모델:

```text
gpt-5.4-mini
```

직접 지정:

```bash
python main.py commit -model gpt-5.4-mini
```

모델별로 지원하는 API 파라미터가 다를 수 있으므로 다른 모델을 사용할 때는 해당 모델의 호환성을 확인해야 합니다.

---

## 11. `-temperature`

사용 범위:

```text
0.0 ~ 2.0
```

예:

```bash
python main.py commit -temperature 0.3
```

`temperature`는 생성 결과의 다양성에 영향을 주는 값입니다.

현재 구현에서는 기본값 `1.0`일 경우 provider 기본값을 사용하기 위해 API 요청 payload에서 `temperature` 필드를 생략합니다.

사용자가 `1.0`이 아닌 값을 직접 지정하면 실제 요청 payload에 `temperature`가 추가됩니다.

```text
-temperature 1.0
→ API payload에서 temperature 생략

-temperature 0.3
→ API payload에 "temperature": 0.3 전달
```

> custom temperature 지원 여부는 모델/provider 조합에 따라 다를 수 있습니다.  
> 지원하지 않는 조합에서는 COPA가 502 provider error를 반환할 수 있습니다.

---

## 12. `-max-tokens`

`max_tokens`는 **AI가 생성하는 출력의 최대 토큰 수**입니다.

입력 토큰까지 포함한 전체 사용량 제한이 아닙니다.

기본값은 명령에 따라 다릅니다.

```text
commit → 800
pr     → 2000
```

Commit은 비교적 짧은 결과가 필요하지만 PR은 `Why`, `What`, `How to Test`까지 생성해야 하므로 더 큰 기본값을 사용합니다.

직접 지정:

```bash
python main.py commit -max-tokens 1200
```

```bash
python main.py pr -max-tokens 3000
```

사용자가 값을 직접 지정하면 기본값보다 사용자가 지정한 값이 우선합니다.

너무 작은 값을 지정하면 모델이 출력을 완료하기 전에 길이 제한에 도달할 수 있으며, 이 경우 다음과 같은 오류가 발생할 수 있습니다.

```text
[ERROR] AI API가 빈 결과를 반환했습니다.
-max-tokens 값을 늘려보세요. finish_reason=length
```

---

## 13. Safe Mode

실행:

```bash
python main.py commit -safe-mode
```

또는:

```bash
python main.py pr -safe-mode
```

Safe Mode는 AI에 전달되는 Git diff가 지나치게 커지는 것을 방지합니다.

현재 구현은:

- unstaged diff의 원본 내용을 최대 200줄까지 유지
- staged diff의 원본 내용을 최대 200줄까지 유지
- 200줄을 초과하면 이후 내용을 생략
- 생략된 경우 마지막에 안내 문구 추가

예:

```text
... [SAFE MODE] 이후 diff 내용은 생략했습니다.
```

따라서 Safe Mode는 **민감정보를 자동 마스킹하는 기능이 아니라 diff 전송량을 제한하는 방식**입니다.

민감정보가 변경 파일에 포함되어 있다면 API 호출 전에 사용자가 diff를 직접 확인해야 합니다.

---

## 14. Commit 생성 규칙

AI에는 다음 형식으로 응답하도록 요청합니다.

```text
COMMIT_TITLE: 커밋 제목
COMMIT_BODY:
- 핵심 변경 사항
- 핵심 변경 사항
```

프롬프트 규칙:

- 제목은 한 줄
- 제목 최대 72자
- 가능하면 50자 이내
- 본문은 1~2개 불릿
- 변경된 파일 또는 모듈을 본문에 1개 이상 언급하도록 요청
- 실제 Git 변경 내용만 사용
- 불필요한 설명/인사말/코드 블록 금지

프로그램이 실제로 검증하는 항목:

- 제목 존재 여부
- 제목 72자 이하
- 본문 존재 여부
- 본문 불릿 1~2개

### 출력 예시

```text
[INFO] Git 변경 사항 수집 완료
[INFO] AI API 요청 1/2
[DONE] 생성 완료

--- Commit Message ---
Git 변경 사항 기반 커밋 메시지 생성 기능 추가

- main.py에 Commit 생성 CLI 흐름 추가
- ai_client.py에 COPA API 호출 기능 추가
----------------------
```

---

## 15. PR 생성 규칙

AI에는 다음 형식으로 응답하도록 요청합니다.

```text
PR_TITLE: PR 제목
PR_BODY:
## Why
- 변경 배경

## What
- 핵심 변경 사항

## How to Test
- 테스트 방법
```

프로그램이 검증하는 항목:

- PR 제목 존재 여부
- PR 제목 최대 80자
- `## Why` 존재
- `## What` 존재
- `## How to Test` 존재
- 각 섹션에 최소 1개 이상의 불릿 존재

### 출력 예시

```text
[INFO] Git 변경 사항 수집 완료
[INFO] AI API 요청 1/2
[DONE] 생성 완료

--- PR Title ---
Git 변경 사항 기반 PR 초안 생성 기능 추가

--- PR Body ---
## Why
- 반복적인 PR 설명 작성을 자동화하기 위해 기능을 추가했습니다.

## What
- Git 변경 사항 수집 기능을 구현했습니다.
- AI API를 이용한 PR 초안 생성 기능을 추가했습니다.

## How to Test
- python main.py pr 명령을 실행해 결과를 확인합니다.
----------------
```

---

## 16. 생성 결과 검증 및 재요청

AI가 항상 정확한 형식으로 응답한다고 보장할 수 없으므로 생성 결과를 프로그램에서 검증합니다.

정상적인 경우:

```text
[INFO] AI API 요청 1/2
[DONE] 생성 완료
```

첫 번째 결과가 형식 검증에 실패하면:

```text
[INFO] AI API 요청 1/2
[WARN] 생성 결과 형식 검증 실패
[INFO] AI API 재요청 2/2
```

기존 AI 결과와 검증 오류 내용을 포함한 보정 프롬프트를 만들어 **한 번만 추가 요청**합니다.

두 번째 결과도 실패하면 오류를 출력하고 종료합니다.

따라서 API 호출 횟수는:

```text
정상 생성 → 1회
형식 재생성 필요 → 최대 2회
```

입니다.

---

## 17. 오류 처리

### API Key가 없는 경우

```text
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
```

### Git 저장소가 아닌 경우

```text
[ERROR] 현재 디렉토리는 Git 저장소가 아닙니다.
```

### Git 명령 실행 실패

Git 실행 파일이 없거나 명령 실행에 실패하면 오류 메시지를 출력합니다.

Git 명령은 최대 10초까지 기다린 뒤 시간 초과로 처리합니다.

### API 네트워크 오류

```text
[ERROR] AI API 네트워크 요청에 실패했습니다: ...
```

### HTTP 오류

HTTP 상태 코드와 가능한 응답 본문을 함께 출력합니다.

502 오류인 경우:

```text
COPA 게이트웨이 또는 모델 파라미터 호환성을 확인하세요.
```

라는 안내를 추가합니다.

### 출력 토큰 부족

AI 응답이 비어 있고 `finish_reason=length`인 경우 `-max-tokens`를 늘리도록 안내합니다.

---

## 18. 수동 테스트 방법

별도의 자동 테스트 코드 없이 아래 순서로 실제 기능을 확인할 수 있습니다.

### 1) CLI 확인

```bash
python main.py --help
```

### 2) 변경 사항 없음 확인

깨끗한 Git 상태에서:

```bash
python main.py commit
```

예상:

```text
[INFO] 변경 사항이 없습니다.
```

### 3) 변경 사항 생성

파일 하나를 수정한 뒤:

```bash
git status --short
```

### 4) Commit 생성

```bash
python main.py commit
```

### 5) PR 생성

```bash
python main.py pr
```

### 6) staged 변경 확인

```bash
git add .
python main.py commit
```

### 7) model 옵션

```bash
python main.py commit -model gpt-5.4-mini
```

### 8) temperature 옵션

```bash
python main.py commit -temperature 0.3
```

### 9) max-tokens 옵션

```bash
python main.py commit -max-tokens 1200
```

### 10) 여러 옵션 동시 사용

```bash
python main.py pr \
  -model gpt-5.4-mini \
  -temperature 0.3 \
  -max-tokens 2500
```

### 11) Safe Mode

```bash
python main.py commit -safe-mode
```

---

## 19. API 요청 구조

사용 API:

```text
POST https://copa.codyssey.kr/v1/chat/completions
```

인증:

```text
Authorization: Bearer <AI_API_KEY>
```

요청 형태:

```json
{
  "model": "gpt-5.4-mini",
  "messages": [
    {
      "role": "user",
      "content": "Git 변경 사항 기반 프롬프트"
    }
  ],
  "max_tokens": 800
}
```

사용자가 custom temperature를 지정하면:

```json
{
  "temperature": 0.3
}
```

필드가 추가됩니다.

---

## 20. 보안 및 비용 주의사항

### API Key

API Key는 반드시 환경변수로 관리합니다.

```bash
export AI_API_KEY="<virtual-key>"
```

코드에 다음처럼 직접 작성하지 않습니다.

```python
api_key = "실제 API Key"
```

### Git diff 민감정보

`git diff`에는 다음과 같은 정보가 포함될 수 있습니다.

- API Key
- 비밀번호
- 개인정보
- 내부 URL
- 인증 토큰

Safe Mode는 **diff 길이만 제한하며 민감정보 자체를 마스킹하지 않습니다.**

API 요청 전에 필요한 경우:

```bash
git diff
git diff --staged
```

로 전송될 변경 내용을 직접 확인하세요.

### 토큰 사용량

`max_tokens`는 출력 토큰 상한입니다.

전체 사용량은 대략 다음과 같이 결정됩니다.

```text
입력 토큰
(Git status + Git diff + 프롬프트)
+
출력 토큰
(AI 생성 결과)
```

따라서 큰 diff를 전송하면 출력이 짧아도 전체 토큰 사용량이 커질 수 있습니다.

필요하면 `-safe-mode`를 사용하세요.

---

## 21. 미션 요구사항 대응

| 미션 요구사항 | 구현 |
| --- | --- |
| Git 변경 파일 확인 | `git status --short` |
| Git 변경 내용 수집 | `git diff`, `git diff --staged` |
| 변경 없음 처리 | API 호출 없이 안내 후 종료 |
| API Key 환경변수 관리 | `AI_API_KEY` |
| AI API 호출 | COPA `/v1/chat/completions` |
| model 옵션 | `-model`, `--model` |
| temperature 옵션 | `-temperature`, `--temperature` |
| max_tokens 옵션 | `-max-tokens`, `--max-tokens` |
| Commit 메시지 생성 | `python main.py commit` |
| PR 제목/본문 생성 | `python main.py pr` |
| Commit 제목 길이 검증 | 최대 72자 |
| PR 제목 길이 검증 | 최대 80자 |
| PR 필수 섹션 검증 | Why / What / How to Test |
| 각 PR 섹션 불릿 검증 | 최소 1개 |
| 검증 실패 처리 | 최대 1회 재생성 |
| 최종 출력 구분 | Commit/PR 전용 헤더 |
| Safe Mode | diff 전송량 제한 |
| API 오류 처리 | 네트워크/HTTP/응답 형식 오류 처리 |

---

## 22. 사용 시 권장 흐름

실제 Commit 메시지를 만들 때는 다음 흐름을 권장합니다.

```bash
# 1. 변경 사항 확인
git status
git diff

# 2. 커밋할 파일을 staging
git add .

# 3. Commit 메시지 초안 생성
python main.py commit

# 4. 생성 결과 검토 후 실제 commit
git commit -m "검토한 커밋 제목"
```

PR 초안은 브랜치의 변경 사항을 확인한 뒤:

```bash
python main.py pr
```

로 생성하고, 출력된 제목/본문을 검토한 뒤 GitHub PR 작성 화면에 적용합니다.

---

## 23. 주의사항

AI가 생성한 Commit 메시지와 PR 본문은 **최종 정답이 아니라 초안**입니다.

반드시 사용자가 다음 항목을 검토한 후 실제 작업에 적용하세요.

- 변경 이유가 실제 의도와 맞는지
- 테스트 방법이 정확한지
- 민감정보가 포함되지 않았는지
- 프로젝트 또는 팀의 Commit/PR 규칙에 맞는지
