# SparkIdea AI

> **좋아하는 것을 오늘 시작할 수 있는 프로젝트 아이디어로 바꾸는 AI 발상 코치**

SparkIdea AI는 사용자가 **학년, 관심사, 주제**를 입력하면 AI가 수준에 맞는 실행 가능한 프로젝트 아이디어와 첫 실행 단계를 제안하는 한국어 웹 서비스입니다.

## 배포 URL

- **Production:** Vercel 배포 후 이곳에 URL을 기록합니다.
- **Repository:** https://github.com/sunhan888/c2-3

## 주요 기능

- 학년·관심사·주제를 받는 아이디어 생성 폼
- `fetch('/api/generate_idea')`로 Python 서버리스 API 호출
- 아이디어 제목, 한 줄 응원, 설명, 3단계 실행 계획, 확장 팁 표시
- 빈 입력 검증
- API 오류·요청 제한·연결 오류·20초 클라이언트 타임아웃 안내
- 소개 / 아이디어 만들기 / 이용 안내의 3개 메뉴 섹션
- 모바일·태블릿·데스크톱 반응형 UI

## 기술 스택

| 구분 | 기술 |
|---|---|
| 프론트엔드 | HTML5, CSS3, Vanilla JavaScript |
| 백엔드 | Python 3.12, Vercel Serverless Function (`api/generate_idea.py`) |
| AI | OpenAI API (`gpt-5-mini` 기본값, 환경 변수로 변경 가능) |
| 배포 | Vercel |
| 형상 관리 | GitHub |

## 프로젝트 구조

```text
sparkidea-ai/
├── index.html                 # 반응형 단일 페이지 UI
├── css/style.css              # 스타일 및 모바일 미디어 쿼리
├── js/app.js                  # 폼 검증, fetch, 로딩·결과·오류 UI
├── api/generate_idea.py       # Vercel Python Serverless Function
├── dev_server.py              # 로컬 정적 파일 + API 확인 서버
├── requirements.txt           # Python 의존성
├── vercel.json                # Vercel 설정
├── SERVICE_PLAN.md            # 제출용 서비스 기획서
├── SCREENSHOT_GUIDE.md        # 제출용 증빙 캡처 가이드
└── .env.example               # 키 이름만 담은 환경 변수 예시
```

## 로컬 실행 방법

### 1. 프로젝트 내려받기

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd sparkidea-ai
```

### 2. Python 패키지 설치

```bash
python3 -m pip install -r requirements.txt
```

### 3. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 만들고 아래처럼 **본인의 OpenAI API 키를 로컬 환경에만** 설정합니다. `.env` 파일은 `.gitignore`에 포함되어 있어 GitHub에 올라가지 않습니다.

```bash
export OPENAI_API_KEY="your_api_key_here"
# 선택 사항: 모델을 바꾸고 싶을 때만 설정
export OPENAI_MODEL="gpt-5-mini"
```

> API 키를 소스 코드, README, Git 커밋, 스크린샷에 적지 마세요.

### 4. 개발 서버 실행

```bash
npm run dev
# 또는 python3 dev_server.py
```

브라우저에서 `http://localhost:3000`을 열어 확인합니다.

## Vercel 배포 방법

1. GitHub에 `sparkidea-ai` 저장소를 만들고 프로젝트 파일을 `main` 브랜치에 올립니다.
2. Vercel에서 **Add New → Project**를 선택하고 해당 GitHub 저장소를 Import합니다.
3. Framework Preset은 **Other**, Root Directory는 저장소 루트로 둡니다. 별도의 Build Command나 Output Directory는 입력하지 않습니다.
4. **Environment Variables**에 다음 키를 추가합니다.

   | Key | Value | 적용 환경 |
   |---|---|---|
   | `OPENAI_API_KEY` | 본인의 OpenAI API 키 | Production, Preview, Development 필요 범위 |
   | `OPENAI_MODEL` | 선택 사항. 미설정 시 `gpt-5-mini` | 필요 시 |

5. **Deploy**를 누릅니다. Vercel은 루트의 정적 파일을 제공하고 `api/generate_idea.py`를 `/api/generate_idea` 함수로 배포합니다.
6. 배포 URL에서 메뉴 이동, 모바일 화면, 정상 AI 결과, 빈 입력 안내를 모두 확인합니다.
7. 배포가 완료되면 이 README 상단의 **Production** URL과 **Repository** URL을 실제 링크로 교체합니다.

## 오류 점검 순서

| 현상 | 먼저 확인할 내용 |
|---|---|
| `404 /api/generate_idea` | 저장소 루트에 `api/generate_idea.py`가 있는지, Vercel Root Directory가 올바른지 확인 |
| `AI 서비스 설정이 아직 완료되지 않았습니다` | Vercel Project Settings → Environment Variables에 `OPENAI_API_KEY`가 있는지 확인 후 재배포 |
| `502/503` 오류 | OpenAI 키의 유효성, 사용량 한도, Vercel Function 로그 확인 |
| 응답이 늦음 | 잠시 후 재시도하고, OpenAI API 상태와 네트워크 확인 |
| 배포한 화면이 이전 버전 | GitHub `main` 브랜치의 최신 커밋과 Vercel Deployment의 커밋 SHA가 같은지 확인 |

## AI 기능 입출력과 실패 처리

- **입력:** `grade`, `interest`, `topic` 문자열
- **출력:** `title`, `tagline`, `summary`, `steps[]`, `tip`
- **빈 입력:** 프론트와 백엔드 모두 `학년, 관심사, 주제를 모두 입력해 주세요.`를 표시합니다.
- **API 오류:** 사용자가 이해할 수 있는 재시도 메시지를 표시하며 API 키와 세부 오류 내용은 노출하지 않습니다.
- **지연:** 브라우저가 20초 후 요청을 취소하고 네트워크 확인·재시도 메시지를 표시합니다.

## 라이선스

학습 및 포트폴리오 제출용 프로젝트입니다.
