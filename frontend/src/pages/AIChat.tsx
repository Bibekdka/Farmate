import { useState } from 'react'
import axios from 'axios'
import { saveChat } from '../services/chatService'

export default function AIChat() {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)

  const askAI = async () => {
    try {
      setLoading(true)

      const res = await axios.post(
        'http://localhost:5000/api/ai',
        {
          message
        }
      )

      const aiResponse = res.data.response
      setResponse(aiResponse)
      await saveChat(message, aiResponse)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-4 bg-gray-100">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">
          Farm AI Assistant
        </h1>

        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="w-full p-4 rounded-xl border"
          rows={5}
          placeholder="Ask about crops, disease, weather..."
        />

        <button
          onClick={askAI}
          className="mt-4 bg-green-600 text-white px-6 py-3 rounded-xl"
        >
          {loading ? 'Thinking...' : 'Ask AI'}
        </button>

        <div className="mt-6 bg-white p-4 rounded-xl shadow">
          {response}
        </div>
      </div>
    </div>
  )
}
