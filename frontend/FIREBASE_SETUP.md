# Firebase Auth 설정 가이드

## 1. Firebase 프로젝트 설정

### 1.1 Firebase 콘솔에서 웹 앱 추가
1. [Firebase 콘솔](https://console.firebase.google.com/)에 접속
2. `taba-roombot` 프로젝트 선택
3. 프로젝트 개요 페이지에서 "웹 앱 추가" 버튼 클릭
4. 앱 닉네임 입력 (예: "roombot-web")
5. "앱 등록" 클릭

### 1.2 Firebase 설정 정보 복사
웹 앱 등록 후 제공되는 설정 정보를 복사하여 `src/lib/firebase.ts` 파일의 `firebaseConfig` 객체를 업데이트하세요:

```typescript
const firebaseConfig = {
  apiKey: "실제_API_KEY",
  authDomain: "taba-roombot.firebaseapp.com",
  projectId: "taba-roombot",
  storageBucket: "taba-roombot.firebasestorage.app",
  messagingSenderId: "354627144676",
  appId: "실제_웹_앱_ID" // Firebase 콘솔에서 제공되는 웹 앱 ID
};
```

## 2. Google 로그인 활성화

### 2.1 Authentication 설정
1. Firebase 콘솔에서 "Authentication" 메뉴 클릭
2. "시작하기" 클릭
3. "로그인 방법" 탭에서 "Google" 선택
4. "사용 설정" 토글 활성화
5. 프로젝트 지원 이메일 선택
6. "저장" 클릭

### 2.2 승인된 도메인 설정
1. Authentication > 설정 > 승인된 도메인
2. 개발 환경의 경우 `localhost` 추가
3. 프로덕션 환경의 경우 실제 도메인 추가

## 3. 환경 변수 설정 (선택사항)

프로덕션 환경에서는 환경 변수를 사용하는 것을 권장합니다:

```bash
# .env.local 파일 생성
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=taba-roombot.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=taba-roombot
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=taba-roombot.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=354627144676
NEXT_PUBLIC_FIREBASE_APP_ID=your_web_app_id
```

## 4. 사용 방법

### 4.1 로그인
- 페이지 상단의 "Google로 로그인" 버튼 클릭
- Google 계정으로 로그인

### 4.2 로그아웃
- 로그인 후 표시되는 "로그아웃" 버튼 클릭

### 4.3 인증 상태 확인
- 로그인하지 않은 사용자는 서비스 이용 불가
- 로그인 후 AI 환각 탐지 기능 사용 가능

## 5. 보안 고려사항

1. **API 키 보안**: Firebase API 키는 공개적으로 사용 가능하지만, 보안 규칙을 통해 서버 측에서 추가 보안 설정 필요
2. **도메인 제한**: 승인된 도메인에서만 로그인 가능하도록 설정
3. **사용자 데이터**: 필요한 경우 Firestore나 Realtime Database를 사용하여 사용자 데이터 저장

## 6. 문제 해결

### 6.1 로그인 실패
- Firebase 콘솔에서 Google 로그인이 활성화되어 있는지 확인
- 승인된 도메인에 현재 도메인이 포함되어 있는지 확인
- 브라우저 콘솔에서 오류 메시지 확인

### 6.2 설정 오류
- `firebaseConfig` 객체의 모든 필드가 올바르게 설정되어 있는지 확인
- Firebase SDK 버전이 최신인지 확인

## 7. 추가 기능

향후 추가할 수 있는 기능들:
- 이메일/비밀번호 로그인
- 소셜 로그인 (Facebook, Twitter 등)
- 사용자 프로필 관리
- 로그인 상태 지속성
- 보안 규칙 설정 