import { Link, useLocation } from 'react-router-dom'
import { Home, MessageSquare, CloudRain, Activity } from 'lucide-react'

export default function BottomNav() {
  const location = useLocation()
  
  const isActive = (path: string) => location.pathname === path

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 pb-safe z-50 md:hidden">
      <div className="flex justify-around items-center h-16 px-4">
        <Link 
          to="/" 
          className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${isActive('/') ? 'text-green-600' : 'text-gray-500 hover:text-green-500'}`}
        >
          <Home size={24} />
          <span className="text-[10px] font-medium">Home</span>
        </Link>
        
        <Link 
          to="/weather" 
          className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${isActive('/weather') ? 'text-green-600' : 'text-gray-500 hover:text-green-500'}`}
        >
          <CloudRain size={24} />
          <span className="text-[10px] font-medium">Weather</span>
        </Link>

        <Link 
          to="/ai" 
          className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${isActive('/ai') ? 'text-green-600' : 'text-gray-500 hover:text-green-500'}`}
        >
          <div className={`p-3 rounded-full -mt-5 shadow-lg ${isActive('/ai') ? 'bg-green-600 text-white' : 'bg-green-500 text-white'}`}>
            <MessageSquare size={24} />
          </div>
          <span className="text-[10px] font-medium">AI Chat</span>
        </Link>

        <Link 
          to="/yield" 
          className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${isActive('/yield') ? 'text-green-600' : 'text-gray-500 hover:text-green-500'}`}
        >
          <Activity size={24} />
          <span className="text-[10px] font-medium">Yield</span>
        </Link>
      </div>
    </div>
  )
}
