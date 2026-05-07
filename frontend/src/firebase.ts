import { initializeApp } from 'firebase/app'
import { getAnalytics } from "firebase/analytics"
import { getPerformance } from "firebase/performance"
import {
  getAuth,
  GoogleAuthProvider
} from 'firebase/auth'

import { getFirestore } from 'firebase/firestore'

const firebaseConfig = {
  apiKey: "AIzaSyDAYD5s48q48g-ftxhVu5lzIA1KoXsVMSg",
  authDomain: "farmate-b3e93.firebaseapp.com",
  projectId: "farmate-b3e93",
  storageBucket: "farmate-b3e93.firebasestorage.app",
  messagingSenderId: "143966806033",
  appId: "1:143966806033:web:a493563594a5456f1ad1b0",
  measurementId: "G-TL45TPRG89"
}

const app = initializeApp(firebaseConfig)
export const analytics = typeof window !== 'undefined' ? getAnalytics(app) : null
export const perf = typeof window !== 'undefined' ? getPerformance(app) : null

export const auth = getAuth(app)
export const provider = new GoogleAuthProvider()
export const db = getFirestore(app)
