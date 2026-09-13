import { useEffect, useState } from "react";
import { useLocalParticipant, useRemoteParticipants } from "@livekit/components-react";

export type AgentAudioState = "idle" | "processing" | "replying";

export function useAgentAudioState(): AgentAudioState {
  const { localParticipant } = useLocalParticipant();
  const remoteParticipants = useRemoteParticipants();
  const [state, setState] = useState<AgentAudioState>("idle");

  useEffect(() => {
    const interval = setInterval(() => {
      const botSpeaking = remoteParticipants.some((p) => p.isSpeaking);
      const userSpeaking = localParticipant?.isSpeaking ?? false;

      if (botSpeaking) setState("replying");
      else if (userSpeaking) setState("processing");
      else setState("idle");
    }, 120);

    return () => clearInterval(interval);
  }, [localParticipant, remoteParticipants]);

  return state;
}