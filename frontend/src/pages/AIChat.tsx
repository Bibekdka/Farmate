import { useState, useEffect, useContext, useRef } from 'react'
import axios from 'axios'
import { API_URL } from '../config/api'
import { saveChatMessage, getChatHistory } from '../services/chatService'
import { trace } from 'firebase/performance'
import { perf } from '../firebase'
import { AuthContext } from '../context/AuthContext'

export default function AIChat() {
  const { user } = useContext(AuthContext)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<{ role: string, content: string }[]>([])
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchHistory = async () => {
      if (user?.uid) {
        const history = await getChatHistory(user.uid)
        // Map history to the new role structure
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
    const newMessages = [...messages, { role: 'user', content: userMsg }]
    setMessages(newMessages)
    
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
      
      await saveChatMessage(user.uid, userMsg, aiResponse)
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

      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !loading && (
          <div className="text-center text-gray-500 mt-10">
            <p>Start a conversation with your Farm AI!</p>
          </div>
        )}
        
        <div className="space-y-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={msg.role === 'user' ? 'text-right' : 'text-left'}
            >
              <div className={`inline-block p-3 rounded-xl shadow-sm ${
                msg.role === 'user' 
                  ? 'bg-green-600 text-white rounded-tr-sm' 
                  : 'bg-white text-gray-800 border border-gray-100 rounded-tl-sm'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="text-left">
              <div className="inline-block bg-white p-3 rounded-xl shadow-sm border border-gray-100 rounded-tl-sm">
                <div className="flex space-x-1 items-center h-5">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </main>

      <footer className="bg-white p-3 border-t">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && askAI()}
            placeholder={user ? "Ask about crops, weather..." : "Please login to chat"}
            disabled={!user || loading}
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500"
          />
          <button
            onClick={askAI}
            disabled={!user || loading || !message.trim()}
            className="bg-green-600 hover:bg-green-700 text-white rounded-full p-2 w-10 h-10 flex items-center justify-center disabled:opacity-50 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </footer>
    </div>
  )
}
