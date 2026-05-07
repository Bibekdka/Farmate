import { useState, useEffect, useContext, useRef } from 'react'
import axios from 'axios'
import { saveChat, getChatHistory } from '../services/chatService'
import { trace } from 'firebase/performance'
import { perf } from '../firebase'
import { AuthContext } from '../context/AuthContext'

export default function AIChat() {
  const { user } = useContext(AuthContext)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<{ role: string, content: string }[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

  useEffect(() => {
    const fetchHistory = async () => {
      if (user?.uid) {
        const history = await getChatHistory(user.uid)
        const formattedHistory = history.flatMap((h: any) => [
          { role: 'user', content: h.question },
          { role: 'assistant', content: h.answer }
        ])
        setMessages(formattedHistory)
      }
    }
    fetchHistory()
  }, [user])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const askAI = async () => {
    if (!message.trim() || !user?.uid) return;
    
    const userMsg = message
    setMessage('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    
    let t = null;
    try {
      setLoading(true)
      
      if (perf) {
        t = trace(perf, 'ask_ai_trace');
        t.start();
      }

      const res = await axios.post(`${API_URL}/api/ai`, { message: userMsg })
      const aiResponse = res.data.response
      
      setMessages(prev => [...prev, { role: 'assistant', content: aiResponse }])
      
      await saveChat(user.uid, userMsg, aiResponse)
    } catch (err) {
      console.error(err)
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I couldn't process that request right now." }])
    } finally {
      if (t) t.stop();
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50 pb-16 md:pb-0">
      <header className="bg-white p-4 shadow-sm z-10 border-b">
        <h1 className="text-xl font-bold text-center text-green-700">Farm AI Assistant</h1>
      </header>

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="bg-white p-12 text-center rounded-2xl shadow-sm border border-gray-100 max-w-md">
          <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Coming Soon!</h2>
          <p className="text-gray-600">
            We are fine-tuning our agricultural AI models to give you the best organic farming advice. Check back shortly for updates.
          </p>
        </div>
      </main>
    </div>
  )
}
