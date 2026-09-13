const API_BASE = "http://localhost:8000";

export interface StartSessionResponse {
  session_id: string;
  room_url: string;
  user_token: string;
}

export async function startSession(): Promise<StartSessionResponse> {
  const res = await fetch(`${API_BASE}/session/start`, { method: "POST" });
  if (!res.ok) throw new Error("failed to start session");
  return res.json();
}

export async function endSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/session/${sessionId}/end`, { method: "POST" });
}

export const WS_BASE = "ws://localhost:8000";