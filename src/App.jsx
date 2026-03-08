import "./App.css";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import Sidebar from "./components/Sidebar";
import TrafficViolationUI from "./components/TrafficViolationUI";


function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Top bar (shows menu button to open/close sidebar) */}
      <div className="sticky top-0 z-30 flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-3">
        <button
          type="button"
          onClick={() => setSidebarOpen((v) => !v)}
          className="inline-flex items-center justify-center rounded-lg border border-gray-200 p-2 text-gray-700 hover:bg-gray-50"
          aria-label={sidebarOpen ? "Close menu" : "Open menu"}
        >
          {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
        <div className="text-sm font-semibold text-gray-900">AI Traffic Dashboard</div>
      </div>

      {/* Content area */}
      <main className={`transition-all ${sidebarOpen ? "md:pl-72" : "md:pl-0"}`}>
        <TrafficViolationUI />
      </main>
    </div>
  );
} 

export default App
