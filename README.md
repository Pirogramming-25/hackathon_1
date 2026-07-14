# hackathon_1
피로그래밍 25기 해커톤 1조 레포입니다.
# 🧭 똑디 (DDOKDI)

> **디지털 사용이 막막한 순간, 화면을 보며 한 단계씩 따라가는 디지털 설명서 플랫폼**

피로그래밍 25기 해커톤 **1조**의 프로젝트입니다.

`똑디`는 **똑똑한 디지털 설명서**를 뜻합니다.  
디지털 서비스 이용에 익숙하지 않은 사용자가 필요한 설명서를 검색하고, 원하는 자료가 없을 때 질문을 등록하며, 유용한 답변을 새로운 설명서로 축적할 수 있도록 만든 웹 서비스입니다.

---

## 🔥 프로젝트 배경

병원 예약, 금융 업무, 정부 서비스 신청처럼 일상에서 필요한 절차가 빠르게 온라인으로 전환되고 있습니다. 그러나 디지털 환경에 익숙하지 않은 사용자에게는 작은 버튼 하나를 찾는 일도 큰 장벽이 됩니다.

기존의 텍스트 중심 안내는 실제 화면에서 어디를 눌러야 하는지 직관적으로 전달하기 어렵고, 같은 문제가 반복해서 질문되는 한계가 있습니다.

똑디는 **화면 이미지와 단계별 설명을 결합**하고, 질문과 답변을 다시 설명서로 전환하여 이러한 문제를 해결하고자 했습니다.

---

## 🔄 서비스 핵심 흐름

```text
🔍 필요한 설명서 검색
          ↓
🖼️ 단계별 이미지 설명서 확인
          ↓
❓ 원하는 설명서가 없으면 질문 등록
          ↓
💬 다른 사용자가 이미지와 함께 답변
          ↓
✅ 질문 작성자가 답변 하나를 설명서로 등록
          ↓
📚 새로운 설명서로 축적되어 다시 검색·활용
```

단순한 Q&A에서 끝나는 것이 아니라, **한 번 해결된 문제를 재사용 가능한 디지털 설명서로 남기는 것**이 똑디의 핵심입니다.

---

## ✨ 주요 기능

### 1. 🔍 설명서 검색 및 단계별 조회

- 설명서 제목, 단계 설명, 카테고리를 기준으로 검색
- 최신순, 도움순, 저장순 정렬
- 페이지네이션을 적용한 설명서 목록
- 설명서별 공개·가족 공개 상태 표시
- 단계 번호와 이미지, 설명을 순서대로 제공
- 단계 내비게이션을 통한 빠른 이동
- 비회원도 전체 공개 설명서 조회 가능

### 2. 📝 이미지 기반 설명서 작성

- 제목, 카테고리, 공개 범위 설정
- 업로드 순서에 따른 단계별 이미지 구성
- 이미지마다 별도의 설명 입력
- 최대 20장의 이미지 등록
- 파일당 최대 5MB 제한
- JPG, JPEG, PNG, WEBP 형식 지원
- 등록 완료 후 생성된 설명서 상세 페이지로 이동

### 3. 🎨 화면 주석 편집

설명서, 질문, 답변에 첨부하는 이미지 위에 사용자가 직접 안내 표시를 추가할 수 있습니다.

- ⭕ 동그라미 표시
- ➡️ 화살표 표시
- 🏷️ 안내 문구 입력
- ↩️ 실행 취소 및 전체 지우기
- 🖼️ 편집 결과를 이미지에 합성하여 서버에 저장
- 🔄 원본 이미지로 복원

### 4. 💬 질문 및 답변

- 제목, 내용, 카테고리로 질문 등록
- 질문당 최대 5장의 이미지와 이미지별 설명 첨부
- 답변당 최대 4장의 이미지와 이미지별 설명 첨부
- 답변 작성자의 답변 수정 및 삭제
- 질문 작성자의 질문 삭제 및 해결 완료 처리
- 해결 완료된 질문에는 추가 답변 등록 제한
- 내가 등록한 질문과 답변 수 확인

### 5. 📘 답변을 설명서로 전환

질문 작성자는 등록된 답변 중 하나를 새로운 설명서로 등록할 수 있습니다.

- 질문 작성자만 설명서 승격 가능
- 하나의 질문에서 하나의 설명서만 생성 가능
- 질문 제목과 카테고리를 설명서 정보로 활용
- 답변 본문을 첫 번째 설명 단계에 포함
- 답변 이미지와 이미지별 설명을 순서대로 복사
- 이미지가 없는 답변도 본문 중심 설명서로 생성

### 6. ❤️ 좋아요 및 저장

- `도움이 됐어요` 버튼으로 설명서 좋아요 토글
- `저장하기` 버튼으로 설명서 스크랩 토글
- 좋아요 수와 저장 수를 목록 정렬에 활용
- 저장한 설명서를 나의 저장소에서 다시 확인

### 7. 👨‍👩‍👧‍👦 가족 연동 및 가족 공개

- 아이디 기반 사용자 검색
- 가족 연동 요청 전송
- 받은 요청과 보낸 요청 조회
- 가족 요청 수락 및 거절
- 연동된 가족 목록 조회
- 가족 연동 해제
- 수락된 가족 관계에 한해 가족 공개 설명서 조회

### 8. 👤 회원 및 마이페이지

- 아이디·이메일 중복 확인
- 이름, 생년월일을 포함한 회원가입
- 세션 기반 로그인 및 로그아웃
- 내 정보 조회 및 수정
- 현재 비밀번호 확인 후 비밀번호 변경
- 내가 만든 설명서 조회
- 내가 등록한 질문 조회
- 저장한 설명서 조회

---

## 🖼️ 이미지 업로드 정책

| 구분 | 최대 개수 | 파일당 용량 | 지원 형식 |
|---|---:|---:|---|
| 설명서 이미지 | 20장 | 5MB | JPG, JPEG, PNG, WEBP |
| 질문 이미지 | 5장 | 5MB | JPG, JPEG, PNG, WEBP |
| 답변 이미지 | 4장 | 5MB | JPG, JPEG, PNG, WEBP |

---

## 👥 팀 구성

| 이름 | 역할 | 주요 담당 |
|---|---|---|
| **신예원** | 팀장 / Frontend | 홈·검색, 설명서 목록·상세, 설명서 작성, 나의 저장소 화면 |
| **김유겸** | Backend | 설명서·단계 이미지, 좋아요·스크랩, 내 설명서·저장한 설명서 API |
| **임현아** | Frontend | 로그인·회원가입, 마이페이지, 회원 정보 수정, 가족 연동 화면 |
| **김민서** | Backend | 회원·세션 인증, 가족 관계 API, 프로젝트 초기 설정 및 데이터 구조 |
| **이주헌** | Backend / Frontend | 질문·답변 API, 답변의 설명서 승격, 질문 관련 화면, 이미지 주석 기능 연동 |

---

## 🛠️ 기술 스택

### ⚙️ Backend

- Python 3.12
- Django 4.2.30
- Django REST Framework 3.16.1
- Django ORM
- Session Authentication
- Pillow

### 🎨 Frontend

- Django Template
- Vanilla JavaScript
- HTML5
- CSS3
- Canvas API
- Google Material Symbols

### 🗄️ Database & Storage

- SQLite: 로컬 개발 환경
- PostgreSQL: `DATABASE_URL` 기반 배포 환경
- Local FileSystem Storage: 로컬 미디어 저장
- Cloudinary: 환경변수 설정 시 배포 미디어 저장

### 🚀 Deployment

- Gunicorn
- WhiteNoise
- Docker
- Docker Compose

### 🤝 Collaboration

- Git
- GitHub
- Notion

---

## 📂 프로젝트 구조

```text
hackathon_1/
├── accounts/                  # 회원가입, 로그인, 사용자 정보
├── families/                  # 가족 검색, 요청, 수락·거절, 연동 해제
├── guides/                    # 설명서, 단계 이미지, 좋아요, 스크랩, 공유
├── questions/                 # 질문, 답변, 상태 변경, 설명서 승격 데이터
├── config/                    # Django 설정, URL, 공통 예외 처리
├── templates/                 # Django 페이지 템플릿
├── static/
│   ├── css/                   # 공통 및 페이지별 스타일
│   └── js/
│       ├── image-annotator.js # 이미지 주석 편집기
│       └── ...                # 페이지별 API 연동 및 UI 로직
├── media/                     # 로컬 업로드 이미지
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

---

## 🧩 주요 데이터 모델

| 모델 | 역할 |
|---|---|
| `User` | 사용자 계정, 이름, 이메일, 생년월일, 화면 모드 정보 |
| `Guide` | 설명서 제목, 카테고리, 공개 범위, 조회 수, 원본 답변 |
| `GuideImage` | 설명서 단계별 이미지, 설명, 순서, 주석 적용 여부 |
| `GuideLike` | 사용자별 설명서 좋아요 |
| `GuideScrap` | 사용자별 설명서 저장 |
| `GuideShare` | 가족 사용자 대상 개별 공유 내역 |
| `Question` | 질문 제목, 내용, 카테고리, 해결 상태 |
| `QuestionImage` | 질문 이미지, 설명, 노출 순서 |
| `Answer` | 질문 답변, 설명서 작성용 선택 여부 |
| `AnswerImage` | 답변 이미지, 설명, 노출 순서 |
| `FamilyRelation` | 사용자 간 가족 요청 및 수락 상태 |

---

## 🖥️ 페이지 구성

| 경로 | 페이지 |
|---|---|
| `/` | 홈 및 설명서 검색 |
| `/guides/` | 설명서 목록 |
| `/guides/<id>/` | 설명서 상세 |
| `/guide-create/` | 설명서 작성 |
| `/questions/` | 질문 목록 |
| `/questions/create/` | 질문 등록 |
| `/questions/<id>/` | 질문 상세 및 답변 작성 |
| `/my-save/` | 나의 저장소 메뉴 |
| `/my-create/` | 내가 만든 설명서 |
| `/my-questions/` | 내가 등록한 질문 |
| `/save-guide/` | 저장한 설명서 |
| `/my-page/` | 마이페이지 |
| `/my-info/` | 회원 정보 수정 |
| `/family-connect/` | 가족 연동 관리 |
| `/login/` | 로그인 |
| `/signup/` | 회원가입 |

---

## 🔌 주요 API

### 🔐 인증 및 회원

| Method | Endpoint | 기능 |
|---|---|---|
| `GET` | `/api/auth/check-username/` | 아이디 중복 확인 |
| `GET` | `/api/auth/check-email/` | 이메일 중복 확인 |
| `POST` | `/api/auth/signup/` | 회원가입 |
| `POST` | `/api/auth/login/` | 로그인 |
| `POST` | `/api/auth/logout/` | 로그아웃 |
| `GET`, `PATCH` | `/api/users/me/` | 내 정보 조회·수정 |
| `PATCH` | `/api/users/me/ui-mode/` | 화면 모드 변경 |

### 📘 설명서

| Method | Endpoint | 기능 |
|---|---|---|
| `GET`, `POST` | `/api/guides/` | 설명서 목록 조회·등록 |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/guides/<id>/` | 설명서 상세·수정·삭제 API |
| `POST` | `/api/guides/<id>/like/` | 좋아요 등록·취소 |
| `POST` | `/api/guides/<id>/scrap/` | 저장 등록·취소 |
| `POST` | `/api/guides/answers/<answer_id>/promote/` | 답변을 설명서로 승격 |
| `GET` | `/api/users/me/guides/` | 내가 만든 설명서 조회 |
| `GET` | `/api/users/me/scraps/` | 저장한 설명서 조회 |

### ❓ 질문 및 답변

| Method | Endpoint | 기능 |
|---|---|---|
| `GET`, `POST` | `/api/questions/` | 질문 목록 조회·등록 |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/questions/<id>/` | 질문 상세·수정·삭제 API |
| `PATCH` | `/api/questions/<id>/status/` | 질문 상태 변경 |
| `POST` | `/api/questions/<id>/answers/` | 답변 등록 |
| `PUT`, `PATCH`, `DELETE` | `/api/answers/<id>/` | 답변 수정·삭제 |
| `PATCH` | `/api/answers/<id>/accept/` | 설명서 작성용 답변 선택 |
| `GET` | `/api/answers/<id>/guide-data/` | 선택 답변의 설명서 작성 데이터 조회 |
| `GET` | `/api/users/me/questions/` | 내가 등록한 질문 조회 |
| `GET` | `/api/users/me/answers/` | 내가 작성한 답변 조회 |

### 👨‍👩‍👧‍👦 가족 연동

| Method | Endpoint | 기능 |
|---|---|---|
| `GET` | `/api/families/users/` | 사용자 검색 |
| `POST` | `/api/families/requests/` | 가족 요청 전송 |
| `GET` | `/api/families/requests/received/` | 받은 가족 요청 조회 |
| `GET` | `/api/families/requests/sent/` | 보낸 가족 요청 조회 |
| `PATCH` | `/api/families/requests/<id>/accept/` | 가족 요청 수락 |
| `PATCH` | `/api/families/requests/<id>/reject/` | 가족 요청 거절 |
| `GET` | `/api/families/` | 연동된 가족 목록 조회 |
| `DELETE` | `/api/families/<id>/` | 가족 연동 해제 |

---

## 📡 공통 API 응답 형식

### ✅ 성공

```json
{
  "success": true,
  "data": {},
  "message": "요청이 성공적으로 처리되었습니다."
}
```

### ❌ 실패

```json
{
  "success": false,
  "data": null,
  "message": "요청 처리에 실패했습니다."
}
```

---

## 💻 로컬 실행 방법

### 1. 저장소 복제

```bash
git clone <REPOSITORY_URL>
cd hackathon_1
```

### 2. 가상환경 생성 및 실행

#### Windows Git Bash

```bash
python -m venv venv
source venv/Scripts/activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 환경변수 파일 생성

```bash
cp .env.example .env
```

기본 환경변수 예시:

```env
DJANGO_SECRET_KEY=local-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

배포 환경에서는 필요에 따라 다음 값을 추가합니다.

```env
DATABASE_URL=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_EMAIL=
DJANGO_SUPERUSER_PASSWORD=
```

### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

### 5. 데이터베이스 적용

```bash
python manage.py migrate
```

### 6. 서버 실행

```bash
python manage.py runserver
```

접속 주소:

```text
http://127.0.0.1:8000/
```

### 7. 테스트

```bash
python manage.py test
```

---

## 🐳 Docker 실행

```bash
cp .env.example .env
docker compose up --build
```

접속 주소:

```text
http://127.0.0.1:8000/
```

---

## ⚙️ 구현상 주요 특징

- 🔐 Django Session Authentication과 CSRF 검증 사용
- 💾 질문, 답변, 설명서 생성 및 이미지 저장 과정에 트랜잭션 적용
- ✅ 한 질문에는 하나의 선택 답변만 존재하도록 데이터베이스 제약조건 적용
- 🔗 답변 원본과 승격된 설명서를 `OneToOneField`로 연결
- 🗑️ 질문·답변 이미지 데이터 삭제 후 실제 저장 파일도 함께 삭제
- 👨‍👩‍👧‍👦 인증 여부와 가족 관계에 따라 설명서 조회 범위를 서버에서 제한
- 📡 공통 예외 처리기를 통해 API 오류 응답 형식 통일

---

## 🎯 프로젝트 목표

똑디는 디지털 서비스 사용법을 단순히 설명하는 데서 끝나지 않습니다.

한 사용자의 질문과 다른 사용자의 답변이 다시 새로운 설명서가 되고, 그 설명서가 또 다른 사람의 어려움을 줄이는 구조를 목표로 합니다.

> **💡 한 사람의 해결 경험을 모두가 따라 할 수 있는 설명서로 만듭니다.**
