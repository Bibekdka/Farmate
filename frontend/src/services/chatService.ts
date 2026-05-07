import {
  addDoc,
  collection,
  serverTimestamp
} from 'firebase/firestore'

import { db } from '../firebase'

export const saveChat = async (
  question: string,
  answer: string
) => {
  await addDoc(collection(db, 'chats'), {
    question,
    answer,
    createdAt: serverTimestamp()
  })
}
