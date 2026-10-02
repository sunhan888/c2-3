# SparkIdea AI 작업 목록

- [ ] **아이디어 생성 경험 구현:** 학년, 관심사, 주제의 필수 입력 폼을 제공하고, 빈 입력에는 "학년, 관심사, 주제를 모두 입력해 주세요."를 표시한다. `fetch('/api/generate_idea')`로 요청해 로딩 상태와 제목·요약·설명·실행 단계·확장 팁의 결과를 화면에 표시한다. 요청이 20초를 넘으면 재시도 안내를, API 오류에는 이해하기 쉬운 오류 안내를 표시한다.
- [ ] **소개·생성·이용 안내의 3개 섹션 구현:** 상단 메뉴가 `#about`, `#generator`, `#guide`로 이동하고, 각 섹션이 서비스 가치·폼·이용 방법을 명확히 전달한다. 모바일과 데스크톱에서 메뉴와 콘텐츠가 정상 표시된다.
- [ ] **Python Vercel Serverless Function 구현:** `api/generate_idea.py`가 POST JSON을 받고 입력을 검증한 뒤 `OPENAI_API_KEY` 및 선택적 `OPENAI_MODEL` 환경 변수로 AI API를 호출한다. API 키가 없거나 공급자 오류가 발생해도 키를 노출하지 않는 JSON 오류 응답을 반환한다.
- [ ] **배포 가능한 프로젝트 패키지 구성:** `requirements.txt`, `vercel.json`, `.env.example`, `.gitignore`, 로컬 확인용 명령을 포함한다. README에는 서비스 소개, 기술 스택, 로컬 실행, Vercel 환경 변수, GitHub·Vercel 배포 절차 및 배포 URL 기록 영역을 포함한다.
- [ ] **제출 문서와 증빙 준비:** 서비스 기획서에 목적·타깃·페이지 구성·핵심 기능·AI 입출력·실패 처리 기준을 포함하고, 데스크톱·모바일·AI 동작·AI 코딩 과정 증빙을 위한 캡처 가이드를 작성한다.
- [ ] **검증 및 배포:** HTML/CSS/JavaScript/Python 진단을 통과하고, 로컬에서 빈 입력·정상 API 흐름·API 키 오류·모바일 레이아웃을 확인한다. GitHub와 Vercel에 연결하여 실제 URL에서 동일한 동작을 확인한다.
