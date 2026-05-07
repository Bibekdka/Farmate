import {
  addDoc,
  collection,
  serverTimestamp,
  query,
  where,
  orderBy,
  getDocs
} from 'firebase/firestore'

import { db } from '../firebase'

export const saveChatMessage = async (
  uid: string,
  question: string,
  answer: string
) => {
  await addDoc(collection(db, 'chats'), {
    uid,
    question,
    answer,
    createdAt: serverTimestamp()
  })
}

export const getChatHistory = async (uid: string) => {
  const q = query(
    collection(db, 'chats'),
    where('uid', '==', uid),
    orderBy('createdAt', 'asc')
  )
  const querySnapshot = await getDocs(q)
  return querySnapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data()
  }))
}
