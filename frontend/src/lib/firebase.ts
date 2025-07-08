import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { getAnalytics } from 'firebase/analytics';

const firebaseConfig = {
  apiKey: "AIzaSyArK4SuyqsnnbNPNHUcSjJx8inNMh9wTqY",
  authDomain: "taba-roombot.firebaseapp.com",
  projectId: "taba-roombot",
  storageBucket: "taba-roombot.appspot.com",
  messagingSenderId: "354627144676",
  appId: "1:354627144676:web:34c47065e613bb370e95f1",
  measurementId: "G-15FFHWBVYS"
};

// Firebase 앱 초기화
const app = initializeApp(firebaseConfig);

// Analytics는 브라우저에서만 초기화
let analytics: ReturnType<typeof getAnalytics> | undefined = undefined;
if (typeof window !== "undefined") {
  analytics = getAnalytics(app);
}

// Auth 서비스 초기화
export const auth = getAuth(app);

// Google Auth Provider 초기화
export const googleProvider = new GoogleAuthProvider();

export default app;
export { analytics };

let isLoggingIn = false;
async function handleLogin() {
  if (isLoggingIn) return;
  isLoggingIn = true;
  try {
    await signInWithPopup(auth, googleProvider);
  } finally {
    isLoggingIn = false;
  }
}

async function sendUserToBackend() {
  const user = auth.currentUser;
  if (!user) return;
  const idToken = await user.getIdToken();
  await fetch('http://localhost:8000/api/save-user', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${idToken}`
    }
  });
} 