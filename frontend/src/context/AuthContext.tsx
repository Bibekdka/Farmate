import {
  createContext,
  useEffect,
  useState
} from 'react'

import {
  signInWithPopup,
  signOut,
  onAuthStateChanged,
  User
} from 'firebase/auth'

import {
  auth,
  provider
} from '../firebase'

export const AuthContext = createContext<any>(null)

export const AuthProvider = ({ children }: any) => {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u)
    })

    return () => unsub()
  }, [])

  const login = async () => {
    await signInWithPopup(auth, provider)
  }

  const logout = async () => {
    await signOut(auth)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
