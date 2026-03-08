import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_KEY = "traffic_dashboard_recent_violations";
const MAX_VIOLATIONS = 50;

function loadStoredViolations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function persistViolations(violations) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(violations));
  } catch {
    // ignore storage failures (private mode/quota)
  }
}

export function useViolationsSocket() {
  const [violations, setViolations] = useState(() => loadStoredViolations());
  const socketRef = useRef(null);

  const addViolation = useCallback((violation) => {
    setViolations((prev) => [violation, ...prev].slice(0, MAX_VIOLATIONS));
  }, []);

  useEffect(() => {
    persistViolations(violations);
  }, [violations]);

  useEffect(() => {
    if (socketRef.current) return; // prevent double connection

    console.log("Connecting to WebSocket...");

    const wsUrl = import.meta.env.VITE_WS_VIOLATIONS_URL || "ws://127.0.0.1:8000/ws/violations";
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket Connected");
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setViolations((prev) => [data, ...prev].slice(0, MAX_VIOLATIONS));
      } catch (_) {
        console.warn("Invalid WebSocket message:", event.data);
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };

    socket.onclose = () => {
      console.log("WebSocket Closed");
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, []);

  return [violations, addViolation];
}
