# Future Universe

청소년이 다양한 진로와 분야를 탐색하고, 현직 전문가에게 직접 질문할 수 있는 진로 탐색 플랫폼입니다.

---

## 목차

- [주요 기능](#주요-기능)
- [화면 구성 (페이지)](#화면-구성-페이지)
- [사용자 역할](#사용자-역할)
- [토큰 시스템](#토큰-시스템)
- [기술 스택](#기술-스택)
- [설치 및 실행](#설치-및-실행)
- [디렉터리 구조](#디렉터리-구조)
- [시드 데이터](#시드-데이터)
- [데이터베이스 스키마](#데이터베이스-스키마)

---

## 주요 기능

### 3D 커리어 유니버스
- 양자역학·AI·기후위기·음악·로보틱스 등 50개 이상의 관심 분야가 3D 구(sphere) 위에 배치된 인터랙티브 맵
- 전문가 노드(별)와 활동 분야 노드(구)가 선으로 연결되어 "어떤 전문가가 어느 분야를 커버하는지" 한눈에 확인
- 승인된 전문가 DB를 실시간으로 반영해 노드 위치·크기·색상을 자동 갱신
- 비로그인 상태에서는 미리보기 레이어(블러 오버레이)로 로그인 유도

### 나만의 우주 (My Universe)
- 학생이 3D 탐색기에서 관심 노드를 클릭해 최대 10개까지 저장
- 저장 상태를 프로필 페이지의 "나만의 우주" 섹션에서 카드 그리드로 확인
- 저장된 관심 노드를 기반으로 AI 진로상담·전문가 추천에 자동 반영
- 학생 로그인 간 상태 동기화 (DB + CSV 시드 파일 동시 갱신)

### 스토리와 미션
- 질문이 아직 많지 않은 분야도 전문가의 실제 이야기와 입문 미션으로 먼저 탐색
- **스토리**: 직업명만으로 알기 어려운 실제 하루, 오해, 일의 방식 등을 카드로 제공
- **미션**: 학생이 5~120분 안에 시도해볼 수 있는 작은 활동을 저장
- 저장한 미션은 학생 프로필의 "저장한 미션" 탭에서 확인
- 전문가는 내 프로필에서 스토리·미션을 등록하고 영향력 지표를 확인

### 전문가 Q&A
- 승인된 현직 전문가(AI 연구원, 응급의학과 전문의, UX 디자이너, SF 작가 등)에게 제목+본문 형식으로 질문
- **공개 Q&A 게시판** — 전체 공개 질문을 전문가 필터·답변 상태 필터·키워드 검색으로 탐색
- **질문하기** — 전문가 선택 → 제목·내용 작성 → 토큰 1,000개 차감 후 등록
- **내 질문** — 내가 보낸 질문과 답변 상태를 토글 형식으로 조회
- 전문가가 답변을 등록하면 학생 프로필에 미확인 답변 배지(🔴) 표시

### AI 진로상담
- OpenAI GPT(gpt-4o-mini) 기반 채팅형 진로 상담
- 학생의 관심 노드와 연결된 전문가 DB를 시스템 프롬프트에 자동 주입해 맞춤 조언 제공
- API 미설정 또는 오류 시 로컬 가이드 모드로 자동 전환 (오류 없이 기본 답변 제공)
- 질문 입력 후 연관 전문가 최대 3명을 추천 카드로 표시, 바로 질문하기 연결

### AI 진로로드맵
- 현재 상태(예: "중학교 2학년, AI에 관심")와 목표 활동 분야를 입력하면 4단계 실행 로드맵 생성
- 관련 전문가 사례(전공 → 직업 경로)를 프롬프트에 포함해 현실적인 경로 제시
- 단계별 expander + 타임라인 시각화(Plotly)로 표시

### 진로 인사이트
- 학생 관심 노드 저장 순위, 전문가 연결 현황, Q&A 흐름을 시각화
- **관심 트렌드** — 관심은 높지만 전문가 연결이 부족한 노드 자동 파악
- **전공-직업 연결** — 전공별로 어떤 직업으로 이어지는지 바 차트·트리맵 제공
- **질문 흐름** — 날짜별 질문 추이, 분야별 질문 수, 미답변 질문 목록

### 진로 탐색 영상
- YouTube 임베드 방식으로 진로 탐색 영상을 2열 카드 그리드로 제공
- 관리자가 영상 URL·제목·설명을 추가/삭제 가능

### 설문조사 (EVENT)
- 학생·교사·학부모·일반인 유형별 맞춤 10문항 (Likert 5점 / 객관식 / 주관식)
- 3단계 흐름 — 기본 정보 → 유형별 문항 → 완료
- 로그인 계정에 연동되어 중복 제출 시 최신 응답으로 갱신

### Contact Us
- 플랫폼 기획자 소개 + 이메일 문의 안내
- 빠른 문의 폼 (문의 유형·내용 입력 → 확인 미리보기)

---

## 화면 구성 (페이지)

| 페이지 | 경로(내부 key) | 접근 권한 |
|--------|----------------|-----------|
| 홈 | `home` | 모두 |
| 3D 유니버스 | `3d` | 로그인 |
| 스토리와 미션 | `discovery` | 로그인 |
| 전문가 Q&A | `questions` | 로그인 |
| AI 진로상담 | `career` | 로그인 |
| 진로 탐색 영상 | `career_videos` | 모두 |
| 설문조사 | `survey` | 로그인 |
| Contact Us | `contact` | 모두 |
| 내 프로필 | `profile` | 로그인 |
| 설문 대시보드 | `admin_dashboard` | 관리자 |
| 섭외 인사이트 | `admin_gap_insights` | 관리자 |
| DB 관리 | `admin_db_viewer` | 관리자 |
| 전문가 승인 관리 | `admin_expert_approval` | 관리자 |

---

## 사용자 역할

### 학생 (student)
- 회원가입 시 학교급·학교명·학년 입력
- 3D 유니버스에서 관심 노드 저장 및 나만의 우주 구성
- 스토리와 미션에서 입문 미션 저장
- 전문가에게 질문 등록 (토큰 소모)
- AI 진로상담·로드맵 이용
- 프로필에서 저장한 미션, 내 질문·답변 현황 확인

### 전문가 (expert)
- 회원가입 시 직함·소속·전공·대분류 분야·활동 노드·소개 입력
- **관리자 승인 후** 3D 유니버스에 노드로 표시, Q&A 답변 가능
- 프로필에서 활동 분야 수정 (수정 시 재승인 필요)
- 목록에 없는 활동 분야를 추가 요청 가능
- 프로필에서 스토리·입문 미션 등록 및 영향력 지표 확인
- 답변 1건 등록 시 토큰 1,000개 적립

### 관리자 (admin)
- 전문가 승인/거절 (거절 시 학생 역할로 자동 전환)
- 활동 분야(노드) 목록 추가·삭제
- 전문가의 활동 분야 추가 요청 승인/거절
- 설문 응답 대시보드 열람 및 CSV 다운로드
- 섭외 인사이트(관심 공백 분야) 확인
- DB 전체 테이블 조회 및 CSV 내보내기
- 진로 탐색 영상 추가·삭제

---

## 토큰 시스템

| 이벤트 | 금액 |
|--------|------|
| 학생 가입 보너스 | +10,000 T |
| 전문가 가입 보너스 | +5,000 T |
| 학생이 질문 등록 | −1,000 T |
| 전문가가 답변 등록 | +1,000 T |

토큰이 1,000개 미만이면 질문을 등록할 수 없습니다. 사용/적립 내역은 프로필 페이지에서 확인할 수 있습니다.

---

## 기술 스택

| 영역 | 사용 기술 |
|------|-----------|
| 프레임워크 | Streamlit |
| 데이터베이스 | SQLite (sqlite3) |
| 3D 시각화 | Three.js (Streamlit Custom Component) |
| AI | OpenAI API — gpt-4o-mini |
| 차트 | Plotly, Matplotlib, WordCloud |
| 인증 | SHA-256 해시 기반 자체 로그인 |
| 폰트 | Pretendard (CDN) |

---

## 설치 및 실행

### 요구사항

- Python 3.9 이상

### 설치

```bash
pip install -r requirements.txt
```

### 환경변수 설정 (선택)

프로젝트 루트에 `.env` 파일 생성:

```
OPENAI_API_KEY=sk-...
```

OpenAI 키 없이도 앱은 실행됩니다. AI 기능은 로컬 가이드 모드로 자동 동작합니다.

### 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속.

첫 실행 시 DB 스키마 초기화 및 `data/seed/` CSV 데이터가 자동으로 로드됩니다.

---

## 디렉터리 구조

```
future_universe/
├── app.py                           # 메인 Streamlit 앱 (단일 파일)
├── requirements.txt
├── runtime.txt                      # Python 버전 명세
├── .env                             # OpenAI API 키 (gitignore 권장)
├── bg_image.png                     # 히어로 배너 배경 이미지
├── future_universe.db               # SQLite DB (첫 실행 시 자동 생성)
├── future_universe_3d.html          # Three.js 3D 유니버스 원본 HTML
├── components/
│   └── future_universe_3d/
│       └── index.html               # Streamlit Custom Component 렌더링용 (자동 생성)
└── data/
    └── seed/
        ├── accounts.csv             # 초기 계정 (login_id, password, role, tokens)
        ├── expert_profiles.csv      # 초기 전문가 프로필
        ├── expert_nodes.csv         # 초기 전문가 활동 분야 매핑
        ├── student_profiles.csv     # 초기 학생 프로필
        ├── student_univers.csv      # 초기 학생 관심 노드 저장 현황
        ├── questions.csv            # 초기 학생 질문
        └── question_answers.csv     # 초기 전문가 답변
```

---

## 시드 데이터

앱 시작 시 `data/seed/` 디렉터리의 CSV 파일을 읽어 DB에 초기 데이터를 자동 삽입합니다. 이미 존재하는 레코드는 무시하고 새 레코드만 추가(`INSERT OR IGNORE`)합니다.

현재 시드에는 20명의 전문가(AI 연구원, 바이오인포매틱스 연구원, UX 디자이너, SF 작가, 생태 탐방 교육가 등)가 포함되어 있으며 모두 승인 완료 상태입니다.

### 초기 관리자 계정

앱 첫 실행 시 관리자가 없으면 자동 생성됩니다.

| 아이디 | 비밀번호 | 역할 |
|--------|---------|------|
| `admin` | `admin1234` | 관리자 |

> 운영 환경에서는 반드시 비밀번호를 변경하세요.

---

## 데이터베이스 스키마

| 테이블 | 설명 |
|--------|------|
| `accounts` | 공통 로그인 — login_id, password_hash, role(student/expert/admin), tokens |
| `student_profiles` | 학생 프로필 — display_name, school_level, school_name, grade |
| `expert_profiles` | 전문가 프로필 — display_name, title, organization, major, current_job, field, description, is_approved |
| `expert_nodes` | 전문가 ↔ 활동 분야(노드) 다대다 매핑 |
| `my_universe` | 학생별 관심 노드 저장 목록 |
| `questions` | 학생 → 전문가 질문 — question_title, question_text, is_public |
| `question_answers` | 전문가 답변 — answer_text, is_new_for_asker |
| `expert_stories` | 전문가 스토리 — title, story_type, body, field_hint |
| `expert_missions` | 전문가 입문 미션 — title, mission_text, difficulty, estimated_minutes |
| `mission_attempts` | 학생별 미션 저장/시도 기록 |
| `token_transactions` | 토큰 적립·차감 내역 |
| `universe_nodes` | 관리자가 추가한 커스텀 노드 목록 |
| `node_requests` | 전문가의 활동 분야 추가 요청 (pending/approved/rejected) |
| `career_videos` | 진로 탐색 YouTube 영상 목록 |
| `survey_participants` | 설문 응답자 기본 정보 |
| `survey_questions` | 유형별(학생/교사/학부모/일반인) 설문 문항 |
| `survey_responses` | 문항별 응답값 |
