import { useEffect } from "react";
import { WS_BASE } from "../api/session";
import { useFinancialStore } from "../store/useFinancialStore";

export function useStateSocket(sessionId: string | null) {
  const applySnapshot = useFinancialStore((s) => s.applySnapshot);
  const applyDiff = useFinancialStore((s) => s.applyDiff);
  const applyTranscript = useFinancialStore((s) => s.applyTranscript);
  const setConnected = useFinancialStore((s) => s.setConnected);
  const applyQuestion= useFinancialStore((s)=> s.applyQuestion);

  useEffect(() => {
    if (!sessionId) return;
    const ws = new WebSocket(`${WS_BASE}/session/${sessionId}/state`);

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === "snapshot") applySnapshot(msg.data);
      else if (msg.type === "diff") applyDiff(msg.data);
      else if (msg.type === "transcript") applyTranscript(msg.data.role, msg.data.text);
      else if (msg.type === "question") applyQuestion(msg.data.question);
    };

    const interval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 15000);

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, [sessionId, applySnapshot, applyDiff, applyTranscript, setConnected]);
}