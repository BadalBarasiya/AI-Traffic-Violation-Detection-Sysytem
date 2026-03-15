import "./App.css";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import Sidebar from "./components/Sidebar";
import TrafficViolationUI from "./components/TrafficViolationUI";
import Login from "./components/Login";

const AUTH_STORAGE_KEY = "traffic_dashboard_auth";

function loadStoredAuth() {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || !parsed.access_token || !parsed.role) return null;
    return parsed;
  } catch {
    return null;
  }
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [auth, setAuth] = useState(() => loadStoredAuth());

  const handleLoginSuccess = (data) => {
    const authData = {
      access_token: data.access_token,
      username: data.username,
      role: data.role,
    };
    setAuth(authData);
    try {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authData));
    } catch {
      // ignore storage issues
    }
  };

  const handleLogout = () => {
    setAuth(null);
    try {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    } catch {
      // ignore
    }
    setSidebarOpen(false);
  };

  if (!auth) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100 px-4">
        <Login onSuccess={handleLoginSuccess} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        user={auth}
        onLogout={handleLogout}
      />

      {/* Top bar (shows menu button to open/close sidebar) */}
      <div className="sticky top-0 z-30 flex items-center justify-between gap-3 border-b border-gray-200 bg-white px-4 py-3">
        <div className="flex items-center gap-3">
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
        <div className="hidden text-xs text-gray-600 md:block">
          Signed in as{" "}
          <span className="font-semibold">
            {auth.username} ({auth.role})
          </span>
        </div>
      </div>

      {/* Content area */}
      <main className={`transition-all ${sidebarOpen ? "md:pl-72" : "md:pl-0"}`}>
        <TrafficViolationUI />
      </main>
    </div>
  );
}

export default App
