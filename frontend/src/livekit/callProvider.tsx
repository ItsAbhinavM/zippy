import { LiveKitRoom, RoomAudioRenderer } from "@livekit/components-react";
import "@livekit/components-styles";
import type { ReactNode } from "react";

export function CallProvider({
  serverUrl,
  token,
  children,
}: {
  serverUrl: string;
  token: string;
  children: ReactNode;
}) {
  return (
    <LiveKitRoom
      serverUrl={serverUrl}
      token={token}
      connect
      audio
      video={false}
      onError={(err) => {
        // this is what was silently disappearing before — now it
        // shows up in the console with the ACTUAL reason (auth
        // failure, wrong URL, expired token, etc.)
        console.error("LiveKit connection error:", err);
      }}
      onConnected={() => {
        console.log("LiveKit room connected successfully");
      }}
      onDisconnected={(reason) => {
        console.warn("LiveKit room disconnected:", reason);
      }}
    >
      <RoomAudioRenderer />
      {children}
    </LiveKitRoom>
  );
}