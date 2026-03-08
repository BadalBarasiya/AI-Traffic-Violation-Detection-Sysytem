import React from "react";
import { LayoutDashboard, ImageUp, ListChecks, X } from "lucide-react";

const NAV_ITEMS = [
  { id: "dashboard", label: "Dashboard", href: "#dashboard", icon: LayoutDashboard },
  { id: "upload", label: "Upload Detection", href: "#upload", icon: ImageUp },
  { id: "recent", label: "Recent Violations", href: "#recent", icon: ListChecks },
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      <div
        className={`fixed inset-0 z-40 bg-black/40 transition-opacity md:hidden ${
          open ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onClose}
        aria-hidden={!open}
      />

      <aside
        className={`fixed left-0 top-0 z-50 flex h-full w-72 flex-col border-r border-gray-200 bg-white shadow-sm transition-transform ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
        aria-label="Sidebar"
      >
        <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4">
          <div>
            <div className="text-sm text-gray-500">AI Traffic</div>
            <div className="text-lg font-bold text-gray-900">Dashboard</div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-900 md:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <nav className="p-3">
          <ul className="space-y-1">
            {NAV_ITEMS.map((item) => (
              <li key={item.id}>
                <a
                  href={item.href}
                  onClick={() => onClose?.()}
                  className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-blue-50 hover:text-blue-700"
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="mt-auto p-4 text-xs text-gray-500">
          Tip: Upload an image to add a violation to the list.
        </div>
      </aside>
    </>
  );
}

