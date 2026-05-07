import { Link } from 'react-router-dom'

export default function Dashboard() {
  return (
    <div className="min-h-screen p-4 bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">
        Farmate Dashboard
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link
          to="/ai"
          className="bg-white p-6 rounded-2xl shadow"
        >
          <h2 className="text-xl font-semibold">
            AI Assistant
          </h2>
          <p>Ask farming questions</p>
        </Link>

        <div className="bg-white p-6 rounded-2xl shadow">
          <h2 className="text-xl font-semibold">
            Weather
          </h2>
          <p>Live weather updates</p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow">
          <h2 className="text-xl font-semibold">
            Yield Tracking
          </h2>
          <p>Monitor crop production</p>
        </div>
      </div>
    </div>
  )
}
