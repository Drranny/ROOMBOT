# Node.js 설치 방법

이 프로젝트를 실행하려면 Node.js가 필요합니다. 아래 방법을 따라 설치하세요.

## 1. nvm(Node Version Manager) 설치
터미널에 아래 명령어를 입력하세요:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
```
설치 후 터미널을 완전히 종료했다가 다시 켜세요.

## 2. Node.js LTS 버전 설치

```bash
nvm install 22
nvm use 22
```

## 3. 설치 확인

```bash
node -v   # v22.17.0 등 버전이 출력되어야 합니다.
npm -v    # 10.9.2 등 버전이 출력되어야 합니다.
npx -v    # npx 버전이 출력되어야 합니다.
```

---

# ROOMBOT 프론트엔드 구조 안내

이 프로젝트는 Next.js + TailwindCSS 기반의 프론트엔드입니다.

## 주요 파일/폴더 설명

### 1. 설정 및 환경 파일 (프로젝트 루트)
- **package.json**: 프로젝트 정보, 의존성(설치된 라이브러리), 실행 스크립트 등 관리
- **package-lock.json**: 의존성의 정확한 버전 정보(협업 시 환경 통일)
- **next.config.js/ts**: Next.js의 전반적인 동작 설정
- **tsconfig.json**: TypeScript 설정
- **postcss.config.js**: TailwindCSS 등 PostCSS 플러그인 설정
- **eslint.config.js**: 코드 스타일, 문법 검사(ESLint) 설정
- **.gitignore**: Git에 올리지 않을 파일/폴더 목록
- **README.md**: 프로젝트 설명 문서
- **next-env.d.ts**: Next.js + TypeScript 타입 지원 파일
- **src/app/globals.css**: 전역 CSS(스타일) 파일

### 2. 실제 화면(UI) 관련 파일 (src/app 내부)
- **src/app/page.tsx**: 루트 경로(`/`)에 해당하는 메인 페이지
- **src/app/폴더명/page.tsx**: `/폴더명` 경로에 해당하는 페이지
- **src/app/components/**: (직접 만들면) 재사용 컴포넌트

---

> 대부분의 루트 파일은 설정/환경 관리용이고, 실제 화면(UI)은 `src/app/` 내부에 있습니다.


## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
