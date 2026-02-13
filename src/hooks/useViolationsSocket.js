import { useEffect, useRef, useState } from "react";

export function useViolationsSocket() {
  const [violations, setViolations] = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    if (socketRef.current) return; // prevent double connection

    console.log("Connecting to WebSocket...");

    const socket = new WebSocket("ws://127.0.0.1:8000/ws/violations");
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket Connected");
    };

    socket.onmessage = (event) => {
      console.log("Received:", event.data);
      const data = JSON.parse(event.data);
      setViolations(prev => [data, ...prev]);
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

  return violations;
}
